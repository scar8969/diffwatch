"""diffwatch — Flask application entry point.

Templates live in the project-root templates/ directory, so the template folder
is passed explicitly; Flask(__name__) alone would look in web/templates/.
The watch list page is templates/index.html (there is no watches.html).
The SQLite file also lives in the project-root instance/ directory.
"""

import datetime

from flask import Flask, jsonify, redirect, render_template, request, url_for

from . import paths
from .models import Snapshot, Watch, db
from .watcher.api import bp
from .watcher.differ import diff
from .watcher.fetcher import fetch

paths.ensure_runtime_dirs()


def build_app():
    """Build the application: configuration, database, then routes."""
    app = Flask(
        __name__, template_folder=str(paths.TEMPLATES_DIR), instance_path=str(paths.INSTANCE_DIR)
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + str(
        paths.INSTANCE_DIR / "changewatch.db"
    )
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.register_blueprint(bp)

    @app.get("/")
    def index():
        return render_template("index.html", watches=Watch.query.order_by(Watch.id.desc()).all())

    @app.post("/add")
    def add_watch_page():
        """Create a watch from the HTML form (the JSON route is POST /api/watches)."""
        url = request.form.get("url", "").strip()
        if not url:
            return redirect(url_for("index"))
        try:
            interval = int(request.form.get("interval", "") or 3600)
        except ValueError:
            interval = 3600
        db.session.add(
            Watch(
                url=url,
                selector=request.form.get("selector", "").strip(),
                interval=interval,
                ignore_pattern=request.form.get("ignore_pattern", "").strip(),
                alert_url=request.form.get("alert_url", "").strip(),
            )
        )
        db.session.commit()
        return redirect(url_for("index"))

    @app.post("/watches/<int:wid>/check")
    def check_page(wid):
        """Same fetch/diff/store cycle as POST /api/watches/<id>/check, from the HTML form."""
        w = Watch.query.get_or_404(wid)
        content, h = fetch(w.url, w.selector)
        changed = h != w.last_hash
        if changed and w.last_hash:
            old = Snapshot.query.filter_by(watch_id=wid).order_by(Snapshot.id.desc()).first()
            diff(old.content if old else "", content)  # exercised for parity with the API
        db.session.add(Snapshot(watch_id=wid, content=content, hash=h))
        w.last_hash = h
        w.last_checked = datetime.datetime.utcnow()
        db.session.commit()
        return redirect(url_for("watch_diff", wid=wid))

    @app.get("/watches/<int:wid>/diff")
    def watch_diff(wid):
        """Human-readable diff page for the last two snapshots of a watch."""
        w = Watch.query.get_or_404(wid)
        snaps = Snapshot.query.filter_by(watch_id=wid).order_by(Snapshot.id.desc()).limit(2).all()
        new = snaps[0].content if snaps else ""
        old = snaps[1].content if len(snaps) > 1 else ""
        return render_template("diff.html", watch=w, changes=diff(old, new))

    @app.get("/api/health")
    def health():
        return jsonify(
            {"status": "ok", "watches": Watch.query.count(), "snapshots": Snapshot.query.count()}
        )

    if __name__ == "__main__":
        app.run(host="0.0.0.0", port=5000)

    return app


app = build_app()
