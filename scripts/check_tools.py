#!/usr/bin/env python3
"""Verify the local tools required to build and test the website."""

import re
import subprocess
import sys


MINIMUM_PYTHON = (3, 12)
HUGO_VERSION = "0.158.0"


def main():
    errors = []
    if sys.version_info < MINIMUM_PYTHON:
        errors.append(f"Python {MINIMUM_PYTHON[0]}.{MINIMUM_PYTHON[1]} or newer is required")

    try:
        output = subprocess.run(
            ["hugo", "version"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as error:
        errors.append(f"Hugo could not be run: {error}")
    else:
        match = re.search(r"\bv(\d+\.\d+\.\d+)\b", output)
        if not match or match.group(1) != HUGO_VERSION:
            found = match.group(1) if match else output
            errors.append(f"Hugo Extended {HUGO_VERSION} is required; found {found}")
        if "+extended" not in output:
            errors.append("Hugo Extended is required; the installed Hugo build is not extended")

    if errors:
        raise SystemExit("\n".join(errors))
    print(f"Tool check passed: Python {sys.version.split()[0]}, Hugo Extended {HUGO_VERSION}")


if __name__ == "__main__":
    main()
