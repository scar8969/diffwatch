import hashlib
from datetime import datetime, timedelta


def tick():
    from ..models import Snapshot, Watch, db
    from .alerts import alert
    from .differ import apply_ignore, diff
    from .fetcher import fetch

    changed = []
    for w in Watch.query.all():
        if w.last_checked and datetime.utcnow() - w.last_checked < timedelta(seconds=w.interval):
            continue
        try:
            content, h = fetch(w.url, w.selector)
            content = apply_ignore(content, w.ignore_pattern)
            h = hashlib.sha256(content.encode()).hexdigest()
            is_change = w.last_hash and h != w.last_hash
            if is_change:
                old = Snapshot.query.filter_by(watch_id=w.id).order_by(Snapshot.id.desc()).first()
                changes = diff(old.content if old else "", content)
                alert(w, changes)
                changed.append(w.id)
            db.session.add(Snapshot(watch_id=w.id, content=content, hash=h))
            w.last_hash = h
            w.last_checked = datetime.utcnow()
            db.session.commit()
        except Exception:
            w.last_checked = datetime.utcnow()
            db.session.commit()
    return changed
