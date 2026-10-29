#!/usr/bin/env python3
"""Check that every requirements/**/*.clauses.toml file is well formed."""
import datetime
import os
import re
import tomllib

import common

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


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
        if "line_start" in clause and "line_end" in clause:
            start, end = clause["line_start"], clause["line_end"]
            if not (is_int(start) and is_int(end)):
                errors.append(where + ": line_start and line_end must be integers")
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


def check(root, files):
    errors, notes = [], []
    targets = [
        f for f in files
        if f.startswith("requirements/") and f.endswith(".clauses.toml")
    ]
    if not targets:
        errors.append("no requirements/**/*.clauses.toml files found")
    for rel in targets:
        try:
            with open(os.path.join(root, rel), "rb") as handle:
                data = tomllib.load(handle)
        except (OSError, tomllib.TOMLDecodeError) as exc:
            errors.append("%s: does not parse: %s" % (rel, exc))
            continue
        file_errors, rows = check_file(rel, data)
        errors.extend(file_errors)
        notes.append("%s: %d rows" % (rel, rows))
    return errors, notes


if __name__ == "__main__":
    common.main("lists", check)
