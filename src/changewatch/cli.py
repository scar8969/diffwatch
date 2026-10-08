"""changewatch command line interface.

Heavy imports (Flask-SQLAlchemy through models.py) happen inside the command
body, so `python cli.py --help` works without the database layer installed.
"""
import argparse

def cmd_add(args):
    from .models import Watch, db
    from ._app import app
    with app.app_context():
        w = Watch(url=args.url, selector=args.selector, interval=args.interval)
        db.session.add(w)
        db.session.commit()
        print(f"watch #{w.id} added")
    return 0

def cmd_list(_args):
    from .models import Watch
    from ._app import app
    with app.app_context():
        for w in Watch.query.order_by(Watch.id).all():
            print(f"#{w.id}  {w.url}  selector={w.selector or '-'}  every {w.interval}s")
    return 0

def main():
    p = argparse.ArgumentParser(prog="changewatch", description="watch web pages for changes")
    sub = p.add_subparsers(dest="cmd")
    a = sub.add_parser("add", help="add a watch")
    a.add_argument("url")
    a.add_argument("--selector", default="")
    a.add_argument("--interval", type=int, default=3600)
    sub.add_parser("list", help="list watches")
    args = p.parse_args()
    if args.cmd == "add":
        return cmd_add(args)
    if args.cmd == "list":
        return cmd_list(args)
    p.print_help()
    return 0
