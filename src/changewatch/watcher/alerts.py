import json
import urllib.request


def alert(watch, changes):
    try:
        payload = json.dumps(
            {
                "url": watch.url,
                "added": changes.get("added", []),
                "removed": changes.get("removed", []),
            }
        ).encode()
        req = urllib.request.Request(
            watch.alert_url,
            data=payload,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=10):
            pass
    except Exception:
        pass
