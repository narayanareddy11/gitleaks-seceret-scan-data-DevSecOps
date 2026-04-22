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

    fetch_result = subprocess.run(
        ["git", "fetch", "--all", "--prune"],
        cwd=dest,
    )
    if fetch_result.returncode != 0:
        print(f"   [ERROR] git fetch --all failed for {label} (exit={fetch_result.returncode})")
        sys.exit(fetch_result.returncode)

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
    parser.add_argument("--original-enabled", action="store_true",
                        help="Clone the original repository")
    parser.add_argument("--duplicate-enabled", action="store_true",
                        help="Clone the duplicate repository")
    parser.add_argument("--original-url")
    parser.add_argument("--original-branch", default="main")
    parser.add_argument("--duplicate-url")
    parser.add_argument("--duplicate-branch", default="main")
    args = parser.parse_args()

    banner("STAGE 1 — CLONE REPOSITORIES")

    for d in ("original", "duplicate"):
        if os.path.exists(d):
            shutil.rmtree(d)
    print("\n[CLEANUP] Removed any previous clone directories.")

    if not args.original_enabled and not args.duplicate_enabled:
        print("\n[SKIP] No repositories were enabled for cloning.")
        return

    if args.original_enabled:
        if not args.original_url:
            parser.error("--original-url is required when --original-enabled is used")
        clone(args.original_url, args.original_branch, "original", "ORIGINAL")
    else:
        print("\n[SKIP] ORIGINAL repository cloning disabled.")

    if args.duplicate_enabled:
        if not args.duplicate_url:
            parser.error("--duplicate-url is required when --duplicate-enabled is used")
        clone(args.duplicate_url, args.duplicate_branch, "duplicate", "DUPLICATE")
    else:
        print("\n[SKIP] DUPLICATE repository cloning disabled.")


if __name__ == "__main__":
    main()
