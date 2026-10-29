#!/usr/bin/env python3
"""Check that both licence files exist and are not empty."""
import os

import common

REQUIRED = ("LICENSE-APACHE", "LICENSE-MIT")


def check(root, files):
    errors = []
    for name in REQUIRED:
        path = os.path.join(root, name)
        if name not in files:
            errors.append(name + ": not tracked or missing")
        elif not os.path.isfile(path) or os.path.getsize(path) == 0:
            errors.append(name + ": empty or missing")
    return errors, ["licence files required: " + ", ".join(REQUIRED)]


if __name__ == "__main__":
    common.main("licence", check)
