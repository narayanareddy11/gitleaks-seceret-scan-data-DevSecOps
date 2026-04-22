#!/usr/bin/env python3
"""Compare tracked files or remote branches between ./original and ./duplicate."""

import argparse
import subprocess
import sys


def banner(title):
    pad = 46
    print(f"\n╔{'═' * pad}╗")
    print(f"║  {title:<{pad - 2}}║")
    print(f"╚{'═' * pad}╝")


def git_set(cmd, cwd):
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def compare_files():
    banner("COMPARE ▸ FILE DIFFERENCE (BRANCH)")

    orig_files = git_set(["git", "ls-files"], "original")
    dup_files  = git_set(["git", "ls-files"], "duplicate")

    only_orig = sorted(orig_files - dup_files)
    only_dup  = sorted(dup_files  - orig_files)
    shared    = len(orig_files & dup_files)

    print(f"\n  [ORIGINAL]  Total tracked files : {len(orig_files)}")
    print(f"  [DUPLICATE] Total tracked files : {len(dup_files)}")

    print("\n  ─── Files ONLY in ORIGINAL ────────────────")
    if only_orig:
        for f in only_orig:
            print(f"    [ORIGINAL-ONLY]  {f}")
    else:
        print("    (none)")

    print("\n  ─── Files ONLY in DUPLICATE ───────────────")
    if only_dup:
        for f in only_dup:
            print(f"    [DUPLICATE-ONLY] {f}")
    else:
        print("    (none)")

    print("\n  ─── Summary ───────────────────────────────")
    print(f"    Files only in ORIGINAL  : {len(only_orig)}")
    print(f"    Files only in DUPLICATE : {len(only_dup)}")
    print(f"    Files matching (shared) : {shared}")
    sys.stdout.flush()


def compare_branches():
    banner("COMPARE ▸ BRANCH DIFFERENCE (ALL BRANCHES)")

    def branch_set(cwd):
        raw = git_set(["git", "branch", "-r"], cwd)
        # Strip 'origin/' prefix and remove HEAD pointer entries
        return {
            b.split("origin/", 1)[-1]
            for b in raw
            if "->" not in b and "HEAD" not in b
        }

    orig_branches = branch_set("original")
    dup_branches  = branch_set("duplicate")

    only_orig = sorted(orig_branches - dup_branches)
    only_dup  = sorted(dup_branches  - orig_branches)

    print("\n  [ORIGINAL]  Remote branches:")
    for b in sorted(orig_branches):
        print(f"    {b}")

    print("\n  [DUPLICATE] Remote branches:")
    for b in sorted(dup_branches):
        print(f"    {b}")

    print("\n  ─── Branches ONLY in ORIGINAL ─────────────")
    if only_orig:
        for b in only_orig:
            print(f"    [ORIGINAL-ONLY]  {b}")
    else:
        print("    (none)")

    print("\n  ─── Branches ONLY in DUPLICATE ────────────")
    if only_dup:
        for b in only_dup:
            print(f"    [DUPLICATE-ONLY] {b}")
    else:
        print("    (none)")
    sys.stdout.flush()


def main():
    parser = argparse.ArgumentParser(
        description="Compare two repos — console output only"
    )
    parser.add_argument(
        "--mode", required=True, choices=["branch", "all-branches"],
        help="branch = compare tracked files; all-branches = compare remote branches",
    )
    args = parser.parse_args()

    if args.mode == "branch":
        compare_files()
    else:
        compare_branches()


if __name__ == "__main__":
    main()
