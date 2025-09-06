#!/usr/bin/env python3
"""
Check that all markdown files in docs/ have version headers.
"""

import os
import sys


def main():
    ROOT = "docs"
    missing = []

    if not os.path.exists(ROOT):
        print(f"Warning: {ROOT} directory not found")
        return

    for dirpath, _, filenames in os.walk(ROOT):
        for f in filenames:
            if not f.endswith(".md"):
                continue
            path = os.path.join(dirpath, f)
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    # Read first ~10 lines to check for version header
                    head = "".join([next(fh, "") for _ in range(10)])
                if "Version:" not in head:
                    missing.append(path)
            except (IOError, UnicodeDecodeError) as e:
                print(f"Warning: Could not read {path}: {e}")
                missing.append(path)

    if missing:
        print("Docs missing `Version:` header:")
        for path in missing:
            print(f"  {path}")
        print("\nPlease add version headers like: <!-- Version: 0.6.0 -->")
        sys.exit(1)

    print("Docs version headers OK.")


if __name__ == "__main__":
    main()
