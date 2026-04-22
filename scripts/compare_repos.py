#!/usr/bin/env python3
"""Compare tracked files, branch lists, and file-content differences."""

import argparse
import difflib
import hashlib
from pathlib import Path
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


def file_hash(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_lines(path):
    try:
        return Path(path).read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return None


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


def compare_changes(show_diff):
    banner("COMPARE ▸ NEW / MISSING / MODIFIED FILES")

    orig_files = git_set(["git", "ls-files"], "original")
    dup_files = git_set(["git", "ls-files"], "duplicate")

    only_orig = sorted(orig_files - dup_files)
    only_dup = sorted(dup_files - orig_files)
    shared = sorted(orig_files & dup_files)

    modified = []
    identical = 0

    for rel_path in shared:
        orig_path = Path("original") / rel_path
        dup_path = Path("duplicate") / rel_path
        if file_hash(orig_path) == file_hash(dup_path):
            identical += 1
            continue
        modified.append(rel_path)

    print(f"\n  Shared files checked : {len(shared)}")
    print(f"  Identical files      : {identical}")
    print(f"  Modified files       : {len(modified)}")
    print(f"  Only in ORIGINAL     : {len(only_orig)}")
    print(f"  Only in DUPLICATE    : {len(only_dup)}")

    print("\n  ─── New / Missing Files ───────────────────")
    if only_orig:
        for rel_path in only_orig:
            print(f"    [ONLY-ORIGINAL]  {rel_path}")
    if only_dup:
        for rel_path in only_dup:
            print(f"    [ONLY-DUPLICATE] {rel_path}")
    if not only_orig and not only_dup:
        print("    (none)")

    print("\n  ─── Modified Shared Files ─────────────────")
    if modified:
        for rel_path in modified:
            print(f"    [MODIFIED] {rel_path}")
    else:
        print("    (none)")

    if show_diff and modified:
        print("\n  ─── File Content Diff Preview ─────────────")
        for rel_path in modified:
            orig_lines = load_lines(Path("original") / rel_path)
            dup_lines = load_lines(Path("duplicate") / rel_path)
            print(f"\n    [DIFF] {rel_path}")
            if orig_lines is None or dup_lines is None:
                print("      Binary or non-UTF8 content; skipping unified diff.")
                continue

            diff = list(
                difflib.unified_diff(
                    orig_lines,
                    dup_lines,
                    fromfile=f"original/{rel_path}",
                    tofile=f"duplicate/{rel_path}",
                    lineterm="",
                )
            )
            if not diff:
                print("      Content differs but no text diff could be produced.")
                continue

            for line in diff[:80]:
                print(f"      {line}")
            if len(diff) > 80:
                print("      ... diff truncated after 80 lines ...")
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
        "--mode", required=True, choices=["branch", "all-branches", "changes"],
        help=(
            "branch = compare tracked file lists; "
            "all-branches = compare remote branches; "
            "changes = compare new, missing, and modified shared files"
        ),
    )
    parser.add_argument(
        "--show-diff",
        action="store_true",
        help="When used with --mode changes, print a unified diff preview for modified text files",
    )
    args = parser.parse_args()

    if args.mode == "branch":
        compare_files()
    elif args.mode == "changes":
        compare_changes(args.show_diff)
    else:
        compare_branches()


if __name__ == "__main__":
    main()
