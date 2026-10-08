import difflib, re

def diff(old, new):
    old_lines = old.splitlines()
    new_lines = new.splitlines()
    sm = difflib.SequenceMatcher(None, old_lines, new_lines)
    added, removed = [], []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "replace":
            removed += old_lines[i1:i2]
            added += new_lines[j1:j2]
        elif tag == "delete":
            removed += old_lines[i1:i2]
        elif tag == "insert":
            added += new_lines[j1:j2]
    return {"added": added, "removed": removed}

def apply_ignore(content, pattern):
    if not pattern:
        return content
    return "\n".join(l for l in content.splitlines() if not re.search(pattern, l))
