#!/usr/bin/env python3
"""Clone the original and duplicate repositories into ./original and ./duplicate."""

import argparse
import os
import shutil
import subprocess
import sys


def banner(title):
    pad = 46
    print(f"\n╔{'═' * pad}╗")
    print(f"║  {title:<{pad - 2}}║")
    print(f"╚{'═' * pad}╝")


def clone(url, branch, dest, label):
    print(f"\n┌─ [{label}] Cloning {'─' * 32}")
    print(f"   URL    : {url}")
    print(f"   Branch : {branch}")

    result = subprocess.run(["git", "clone", "--branch", branch, url, dest])
    if result.returncode != 0:
        print(f"   [ERROR] git clone failed for {label} (exit={result.returncode})")
        sys.exit(result.returncode)

    commits = subprocess.run(
        ["git", "rev-list", "--count", "HEAD"],
        cwd=dest, capture_output=True, text=True,
    ).stdout.strip()

    files = subprocess.run(
        ["git", "ls-files"],
        cwd=dest, capture_output=True, text=True,
    ).stdout.strip()
    file_count = len(files.splitlines()) if files else 0

    print(f"   Total commits : {commits}")
    print(f"   Total files   : {file_count}")
    print(f"└{'─' * 48}")


def main():
    parser = argparse.ArgumentParser(description="Clone original and duplicate repos")
    parser.add_argument("--original-url",    required=True)
    parser.add_argument("--original-branch", default="main")
    parser.add_argument("--duplicate-url",   required=True)
    parser.add_argument("--duplicate-branch", default="main")
    args = parser.parse_args()

    banner("STAGE 1 — CLONE REPOSITORIES")

    for d in ("original", "duplicate"):
        if os.path.exists(d):
            shutil.rmtree(d)
    print("\n[CLEANUP] Removed any previous clone directories.")

    clone(args.original_url,  args.original_branch,  "original",  "ORIGINAL")
    clone(args.duplicate_url, args.duplicate_branch, "duplicate", "DUPLICATE")


if __name__ == "__main__":
    main()
