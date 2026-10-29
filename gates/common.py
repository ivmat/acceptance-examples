"""Shared helpers for the gate checks. Pure standard library."""
import os
import subprocess
import sys

GATES_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(GATES_DIR)
FIXTURES = os.path.join(GATES_DIR, "fixtures")

# Paths that the real scans skip. Fixtures hold deliberately bad content.
SKIP_PREFIXES = ("gates/fixtures/",)


def tracked_files(root=ROOT):
    """Return tracked and staged files as repo-relative paths."""
    out = subprocess.run(
        ["git", "ls-files", "--cached", "-z"],
        cwd=root, check=True, capture_output=True,
    ).stdout.decode("utf-8")
    files = [p for p in out.split("\0") if p]
    return sorted(p for p in files if not p.startswith(SKIP_PREFIXES))


def walk_files(root):
    """Return all files under root as sorted relative paths with '/' separators."""
    found = []
    for base, _dirs, names in os.walk(root):
        for name in names:
            rel = os.path.relpath(os.path.join(base, name), root)
            found.append(rel.replace(os.sep, "/"))
    return sorted(found)


def read_text(root, rel):
    """Return the text of a file, or None if it is missing or binary."""
    path = os.path.join(root, rel)
    if not os.path.isfile(path):
        return None
    with open(path, "rb") as handle:
        data = handle.read()
    if b"\0" in data:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return None


def run_check(name, check, argv):
    """Run check(root, files) on the repo, or its selftest with --selftest.

    A check is a function that returns (errors, notes). Errors are strings.
    """
    if "--selftest" in argv:
        return selftest(name, check)
    errors, notes = check(ROOT, tracked_files())
    for note in notes:
        print(note)
    for err in errors:
        print("  " + err)
    return 1 if errors else 0


def selftest(name, check):
    """Run the check on its bad and good fixtures.

    Every file in bad/ must produce an error that names it.
    A file whose name starts with an underscore is a support file and is skipped.
    The good tree must produce no error and must hold at least one file.
    """
    bad_root = os.path.join(FIXTURES, name, "bad")
    good_root = os.path.join(FIXTURES, name, "good")
    failures = []
    bad_files = walk_files(bad_root)
    good_files = walk_files(good_root)
    if not bad_files or not good_files:
        failures.append("fixtures missing for " + name)
    bad_errors, _ = check(bad_root, bad_files)
    for rel in bad_files:
        if os.path.basename(rel).startswith("_"):
            continue  # support file, not expected to fail
        if not any(rel in e for e in bad_errors):
            failures.append("bad fixture not rejected: " + rel)
    if not bad_errors:
        failures.append("bad tree passed")
    good_errors, _ = check(good_root, good_files)
    if good_errors:
        failures.append("good tree failed: " + "; ".join(good_errors))
    for failure in failures:
        print("  selftest " + name + ": " + failure)
    return 1 if failures else 0


def main(name, check):
    sys.exit(run_check(name, check, sys.argv[1:]))
