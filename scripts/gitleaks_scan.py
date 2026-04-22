#!/usr/bin/env python3
"""Run gitleaks on a cloned repository and stream findings to Jenkins console only.

Exit code is always 0 — findings are printed as warnings, not build failures.
"""

import argparse
import subprocess
import sys


def banner(*lines):
    pad = 46
    print(f"\n╔{'═' * pad}╗")
    for line in lines:
        print(f"║  {line:<{pad - 2}}║")
    print(f"╚{'═' * pad}╝")


def scan(repo_dir, label, mode, branch):
    if mode == "branch":
        banner(
            f"GITLEAKS ▸ {label} ▸ BRANCH SCAN",
            f"Branch : {branch}",
        )
        log_opt = f"origin/{branch}"
        print(f"\n  Scanning commits reachable from origin/{branch} ...")
        print(f"  Command: gitleaks detect --source=. --log-opts={log_opt} --verbose")
    else:
        banner(
            f"GITLEAKS ▸ {label} ▸ FULL HISTORY SCAN",
            "Scanning ALL commits across ALL branches",
        )
        log_opt = "--all"
        print(f"\n  Command: gitleaks detect --source=. --log-opts=--all --verbose")

    print()
    sys.stdout.flush()

    # Stream gitleaks output directly to Jenkins console (no capture)
    result = subprocess.run(
        ["gitleaks", "detect", "--source", ".", f"--log-opts={log_opt}", "--verbose"],
        cwd=repo_dir,
    )

    if result.returncode == 0:
        print(f"\n  [RESULT] No secrets found in {label} {mode.upper().replace('-', ' ')} SCAN")
    else:
        print(
            f"\n  [RESULT] Secrets/findings detected in {label} "
            f"{mode.upper().replace('-', ' ')} SCAN (exit={result.returncode})"
        )
    sys.stdout.flush()


def main():
    parser = argparse.ArgumentParser(
        description="Run gitleaks scan — console output only, never fails the build"
    )
    parser.add_argument("--repo-dir", required=True,
                        help="Path to cloned repo directory (e.g. original, duplicate)")
    parser.add_argument("--label",    required=True,
                        help="Display label: ORIGINAL or DUPLICATE")
    parser.add_argument("--mode",     required=True, choices=["branch", "full-history"],
                        help="branch = single branch scan; full-history = --all commits")
    parser.add_argument("--branch",   default="main",
                        help="Branch name used for branch-mode --log-opts (default: main)")
    args = parser.parse_args()

    scan(args.repo_dir, args.label, args.mode, args.branch)


if __name__ == "__main__":
    main()
