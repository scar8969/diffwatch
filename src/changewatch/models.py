from flask_sqlalchemy import SQLAlchemy

from .clock import utcnow

db = SQLAlchemy()


class Watch(db.Model):
    __tablename__ = "watches"
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(512), default="")
    selector = db.Column(db.String(128), default="")
    interval = db.Column(db.Integer, default=3600)
    ignore_pattern = db.Column(db.String(256), default="")
    alert_url = db.Column(db.String(512), default="")
    last_hash = db.Column(db.String(64), default="")
    last_checked = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow)


class Snapshot(db.Model):
    __tablename__ = "snapshots"
    id = db.Column(db.Integer, primary_key=True)
    watch_id = db.Column(db.Integer, db.ForeignKey("watches.id"), index=True)
    content = db.Column(db.Text, default="")
    hash = db.Column(db.String(64), default="")
    at = db.Column(db.DateTime, default=utcnow)
