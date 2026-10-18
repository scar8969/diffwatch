"""B3 changewatch — tests. Run: pytest test_diffwatch.py"""


def test_normalize():
    from changewatch.watcher.fetcher import normalize

    assert normalize("a\n  b\t c") == "a b c"


def test_diff_added_removed():
    from changewatch.watcher.differ import diff

    d = diff("line1\nline2", "line1\nline3")
    assert "line2" in d["removed"]
    assert "line3" in d["added"]


def test_diff_no_change():
    from changewatch.watcher.differ import diff

    d = diff("same", "same")
    assert d["added"] == [] and d["removed"] == []


def test_apply_ignore():
    from changewatch.watcher.differ import apply_ignore

    out = apply_ignore("price: 99\nrandom: 42", "random")
    assert "random" not in out
    assert "price" in out
