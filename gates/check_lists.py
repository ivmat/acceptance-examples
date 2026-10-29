#!/usr/bin/env python3
"""Check that every requirements/**/*.clauses.toml file is well formed.

Every row needs an id, a title, a source, a force and a line range.
The force comes from FORCES below. The line numbers are positive integers
and the start is not after the end.
Three cross-file checks run as well:
- every `row` id in a bindings/**/*.toml map exists in a list;
- every row count that a README states for a list matches the list;
- every method count and source count that a README states matches the list.
A README states a count in one of these forms:
  [x.clauses.toml](x.clauses.toml) ... contains N rows[: A from `a.rst` and B from `b.rst`]
  Methods of `x.clauses.toml`: name N, name N
"""
import collections
import datetime
import os
import posixpath
import re
import tomllib

import common

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# The force values that the lists in this repository use.
FORCES = (
    "MUST", "MUST NOT", "SHOULD", "SHOULD NOT", "MAY",
    "grammar", "guidance", "observation",
)

ROWS_RE = re.compile(r"\[([\w.\-]+\.clauses\.toml)\]\([^)]*\)[^.\n]*?contains (\d+) rows")
FROM_RE = re.compile(r"(\d+) from `([\w.\-]+)`")
METHODS_RE = re.compile(r"^[-* ]*Methods of `([\w.\-]+\.clauses\.toml)`: (.+)$", re.MULTILINE)


def is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def parse_date(value):
    """Return a date for an ISO date string or date value, else None."""
    if isinstance(value, datetime.datetime):
        return None
    if isinstance(value, datetime.date):
        return value
    if isinstance(value, str) and DATE_RE.match(value):
        try:
            return datetime.date.fromisoformat(value)
        except ValueError:
            return None
    return None


def check_file(rel, data):
    errors = []
    standard = data.get("standard")
    if not isinstance(standard, dict) or not standard.get("id"):
        errors.append(rel + ": [standard] has no id")
    clauses = data.get("clause")
    if not isinstance(clauses, list) or not clauses:
        errors.append(rel + ": no [[clause]] rows")
        return errors, 0
    seen = {}
    for index, clause in enumerate(clauses, start=1):
        where = "%s: clause #%d" % (rel, index)
        cid = clause.get("id")
        if not cid or not isinstance(cid, str):
            errors.append(where + ": missing id")
        else:
            where = "%s: clause %s" % (rel, cid)
            if cid in seen:
                errors.append(where + ": duplicate id (first at #%d)" % seen[cid])
            else:
                seen[cid] = index
        if not clause.get("title") or not isinstance(clause.get("title"), str):
            errors.append(where + ": missing title")
        if not clause.get("source") or not isinstance(clause.get("source"), str):
            errors.append(where + ": missing source")
        force = clause.get("force")
        if force is None:
            errors.append(where + ": missing force")
        elif force not in FORCES:
            errors.append(where + ": force %r is not one of %s" % (force, ", ".join(FORCES)))
        start, end = clause.get("line_start"), clause.get("line_end")
        if start is None or end is None:
            errors.append(where + ": line_start and line_end are required")
        elif not (is_int(start) and is_int(end)):
            errors.append(where + ": line_start and line_end must be integers")
        elif start < 1 or end < 1:
            errors.append(where + ": line_start and line_end must be positive")
        elif start > end:
            errors.append(where + ": line_start %d is after line_end %d" % (start, end))
        dates = {}
        for key in ("in_force_from", "in_force_to"):
            if key in clause:
                parsed = parse_date(clause[key])
                if parsed is None:
                    errors.append(where + ": %s is not an ISO date" % key)
                else:
                    dates[key] = parsed
        if len(dates) == 2 and dates["in_force_from"] > dates["in_force_to"]:
            errors.append(where + ": in_force_from is after in_force_to")
    return errors, len(clauses)


def load_toml(root, rel):
    with open(os.path.join(root, rel), "rb") as handle:
        return tomllib.load(handle)


def check_bindings(root, files, all_ids):
    errors, checked = [], 0
    for rel in files:
        if not (rel.startswith("bindings/") and rel.endswith(".toml")):
            continue
        try:
            data = load_toml(root, rel)
        except (OSError, tomllib.TOMLDecodeError) as exc:
            errors.append("%s: does not parse: %s" % (rel, exc))
            continue
        for index, entry in enumerate(data.get("map", []), start=1):
            row = entry.get("row") if isinstance(entry, dict) else None
            if not row or not isinstance(row, str):
                errors.append("%s: map #%d has no row id" % (rel, index))
                continue
            checked += 1
            if row not in all_ids:
                errors.append("%s: map row %s is not in any list" % (rel, row))
    return errors, checked


def check_readme_counts(root, files, lists):
    """lists maps a list path to its parsed clauses."""
    errors, checked = [], 0
    for rel in files:
        if posixpath.basename(rel) != "README.md" or not rel.startswith("requirements/"):
            continue
        text = common.read_text(root, rel)
        if text is None:
            continue
        folder = posixpath.dirname(rel)
        for line in text.splitlines():
            match = ROWS_RE.search(line)
            if not match:
                continue
            name, stated = match.group(1), int(match.group(2))
            target = posixpath.join(folder, name)
            if target not in lists:
                errors.append("%s: names a list that is not tracked: %s" % (rel, target))
                continue
            checked += 1
            actual = len(lists[target])
            if stated != actual:
                errors.append("%s: states %d rows for %s but the file has %d" % (rel, stated, target, actual))
            sources = collections.Counter(posixpath.basename(c.get("source", "")) for c in lists[target])
            for count, src in FROM_RE.findall(line):
                if int(count) != sources.get(src, 0):
                    errors.append("%s: states %s rows from %s in %s but the file has %d"
                                  % (rel, count, src, target, sources.get(src, 0)))
        for match in METHODS_RE.finditer(text):
            name, body = match.group(1), match.group(2)
            target = posixpath.join(folder, name)
            if target not in lists:
                errors.append("%s: names a list that is not tracked: %s" % (rel, target))
                continue
            checked += 1
            actual = collections.Counter(c.get("method") for c in lists[target])
            stated = {}
            for item in body.split(","):
                parts = item.strip().rsplit(" ", 1)
                if len(parts) != 2 or not parts[1].isdigit():
                    errors.append("%s: cannot read method count %r for %s" % (rel, item.strip(), target))
                    continue
                stated[parts[0]] = int(parts[1])
            if stated != dict(actual):
                errors.append("%s: states methods %s for %s but the file has %s"
                              % (rel, dict(sorted(stated.items())), target, dict(sorted(actual.items()))))
    return errors, checked


def check(root, files):
    errors, notes = [], []
    targets = [
        f for f in files
        if f.startswith("requirements/") and f.endswith(".clauses.toml")
    ]
    if not targets:
        errors.append("no requirements/**/*.clauses.toml files found")
    lists = {}
    all_ids = set()
    for rel in targets:
        try:
            data = load_toml(root, rel)
        except (OSError, tomllib.TOMLDecodeError) as exc:
            errors.append("%s: does not parse: %s" % (rel, exc))
            continue
        file_errors, rows = check_file(rel, data)
        errors.extend(file_errors)
        notes.append("%s: %d rows" % (rel, rows))
        clauses = [c for c in data.get("clause", []) if isinstance(c, dict)]
        lists[rel] = clauses
        all_ids.update(c["id"] for c in clauses if isinstance(c.get("id"), str))
    bind_errors, bound = check_bindings(root, files, all_ids)
    errors.extend(bind_errors)
    notes.append("binding map rows checked: %d" % bound)
    count_errors, counted = check_readme_counts(root, files, lists)
    errors.extend(count_errors)
    notes.append("README counts checked: %d" % counted)
    return errors, notes


if __name__ == "__main__":
    common.main("lists", check)
