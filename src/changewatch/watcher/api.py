import datetime

from flask import Blueprint, jsonify, request

from ..models import Snapshot, Watch, db
from .differ import diff
from .fetcher import fetch

bp = Blueprint("watcher", __name__)


@bp.post("/api/watches")
def add_watch():
    d = request.get_json(force=True, silent=True) or {}
    w = Watch(
        url=d.get("url", ""),
        selector=d.get("selector", ""),
        interval=d.get("interval", 3600),
        ignore_pattern=d.get("ignore_pattern", ""),
        alert_url=d.get("alert_url", ""),
    )
    db.session.add(w)
    db.session.commit()
    return jsonify({"id": w.id})


@bp.get("/api/watches")
def list_watches():
    return jsonify(
        {
            "watches": [
                {
                    "id": w.id,
                    "url": w.url,
                    "selector": w.selector,
                    "last_checked": w.last_checked.isoformat() if w.last_checked else "",
                    "changed": bool(w.last_hash),
                }
                for w in Watch.query.all()
            ]
        }
    )


@bp.post("/api/watches/<int:wid>/check")
def manual_check(wid):
    w = Watch.query.get_or_404(wid)
    content, h = fetch(w.url, w.selector)
    changed = h != w.last_hash
    if changed and w.last_hash:
        old = Snapshot.query.filter_by(watch_id=wid).order_by(Snapshot.id.desc()).first()
        changes = diff(old.content if old else "", content)
    else:
        changes = {"added": [], "removed": []}
    db.session.add(Snapshot(watch_id=wid, content=content, hash=h))
    w.last_hash = h
    w.last_checked = datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
    db.session.commit()
    return jsonify({"changed": changed, **changes})


@bp.get("/api/watches/<int:wid>/snapshots")
def snapshots(wid):
    return jsonify(
        {
            "snapshots": [
                {"id": s.id, "at": s.at.isoformat() if s.at else "", "hash": s.hash}
                for s in Snapshot.query.filter_by(watch_id=wid)
                .order_by(Snapshot.id.desc())
                .limit(20)
                .all()
            ]
        }
    )
