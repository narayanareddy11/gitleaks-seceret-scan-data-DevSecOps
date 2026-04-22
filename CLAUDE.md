# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This repository contains a single Jenkins declarative pipeline (`Jenkinsfile`) that performs two functions against a pair of GitHub repositories:

1. **Secret scanning** — runs `gitleaks detect` on each repo (branch scan and/or full `--all` history scan)
2. **Repository comparison** — diffs tracked files and/or remote branches between the two repos

All output is console-only; no JSON reports or archived artifacts are produced.

## Pipeline Parameters

| Parameter | Type | Default | Purpose |
|---|---|---|---|
| `ORIGINAL_REPO_URL` | string | narayanareddy11/scalable-jenkins-kubernetes-dynamic-agents | Source repo to clone |
| `ORIGINAL_BRANCH` | string | `main` | Branch to clone/scan |
| `DUPLICATE_REPO_URL` | string | narayanareddy11/devops-mcp-toolkit | Repo to compare against |
| `DUPLICATE_BRANCH` | string | `main` | Branch to clone/scan |
| `ORIGINAL_BRANCH_SCAN` | bool | true | Run gitleaks on original branch |
| `DUPLICATE_BRANCH_SCAN` | bool | true | Run gitleaks on duplicate branch |
| `ORIGINAL_FULL_HISTORY` | bool | false | Run gitleaks `--all` on original |
| `DUPLICATE_FULL_HISTORY` | bool | false | Run gitleaks `--all` on duplicate |
| `BRANCH_COMPARE` | bool | true | Diff tracked files between default branches |
| `ALL_BRANCH_COMPARE` | bool | false | List branch differences across all remote branches |

## Stage Flow

```
Stage 1: Clone Repositories
  → clones both repos into ./original and ./duplicate workspace dirs

Stage 2: Gitleaks — Original Repo   (skipped if both ORIGINAL_* flags are false)
  → branch scan:  gitleaks detect --log-opts=origin/<branch>
  → history scan: gitleaks detect --log-opts=--all

Stage 3: Gitleaks — Duplicate Repo  (skipped if both DUPLICATE_* flags are false)
  → same pattern as Stage 2

Stage 4: Repository Comparison       (skipped if both COMPARE flags are false)
  → BRANCH_COMPARE:     diff git ls-files output between the two repos
  → ALL_BRANCH_COMPARE: diff git branch -r output between the two repos

post/always: prints summary banner, then rm -rf original duplicate
```

## Key Behaviors

- Gitleaks non-zero exit codes are caught manually (`EXIT_CODE=$?`) so that secret findings do **not** automatically fail the pipeline — findings are reported as warnings in the console output.
- The `BRANCH_COMPARE` stage uses bash process substitution (`<(...)`) so the shebang `#!/bin/bash` is required on those `sh` blocks.
- Cleanup (`rm -rf original duplicate`) always runs in the `post` block regardless of pipeline outcome.

## Jenkins Agent Requirement

- The agent must have `git` and `gitleaks` available on `$PATH`.
- No special credentials block is configured — repos must be publicly accessible or the agent must have pre-configured SSH/token access.
