pipeline {
    agent any

    // ─────────────────────────────────────────────
    // REPOSITORY INPUTS + EXECUTION CONTROLS
    // ─────────────────────────────────────────────
    parameters {
        // Repository inputs
        string(
            name:         'ORIGINAL_REPO_URL',
            defaultValue: 'https://github.com/narayanareddy11/scalable-jenkins-kubernetes-dynamic-agents',
            description:  'Original Repository URL'
        )
        string(
            name:         'ORIGINAL_BRANCH',
            defaultValue: 'main',
            description:  'Original Repository Branch'
        )
        string(
            name:         'DUPLICATE_REPO_URL',
            defaultValue: 'https://github.com/narayanareddy11/devops-mcp-toolkit',
            description:  'Duplicate Repository URL'
        )
        string(
            name:         'DUPLICATE_BRANCH',
            defaultValue: 'main',
            description:  'Duplicate Repository Branch'
        )

        // Gitleaks controls
        booleanParam(name: 'ORIGINAL_BRANCH_SCAN',  defaultValue: true,  description: '[GITLEAKS] Scan original branch')
        booleanParam(name: 'DUPLICATE_BRANCH_SCAN', defaultValue: true,  description: '[GITLEAKS] Scan duplicate branch')
        booleanParam(name: 'ORIGINAL_FULL_HISTORY', defaultValue: false, description: '[GITLEAKS] Scan original full history (--all commits)')
        booleanParam(name: 'DUPLICATE_FULL_HISTORY',defaultValue: false, description: '[GITLEAKS] Scan duplicate full history (--all commits)')

        // Compare controls
        booleanParam(name: 'BRANCH_COMPARE',     defaultValue: true,  description: '[COMPARE] Compare files between branches')
        booleanParam(name: 'ALL_BRANCH_COMPARE', defaultValue: false, description: '[COMPARE] Compare all remote branches')
    }

    // ─────────────────────────────────────────────
    // OUTPUT MODE: CONSOLE_ONLY
    // No reports, no JSON, no archived artifacts
    // ─────────────────────────────────────────────

    stages {

        // ══════════════════════════════════════════
        // STAGE 1 — CLONE REPOSITORIES
        // ══════════════════════════════════════════
        stage('Clone Repositories') {
            steps {
                sh '''
                    echo ""
                    echo "╔══════════════════════════════════════════════╗"
                    echo "║         STAGE 1 — CLONE REPOSITORIES        ║"
                    echo "╚══════════════════════════════════════════════╝"
                    rm -rf original duplicate
                    echo "[CLEANUP] Removed any previous clone directories."
                '''
                sh """
                    echo ""
                    echo "┌─ [ORIGINAL] Cloning ─────────────────────────"
                    echo "   URL    : ${params.ORIGINAL_REPO_URL}"
                    echo "   Branch : ${params.ORIGINAL_BRANCH}"
                    git clone --branch ${params.ORIGINAL_BRANCH} ${params.ORIGINAL_REPO_URL} original
                    echo "   Total commits : \$(cd original && git rev-list --count HEAD)"
                    echo "   Total files   : \$(cd original && git ls-files | wc -l | tr -d ' ')"
                    echo "└──────────────────────────────────────────────"
                """
                sh """
                    echo ""
                    echo "┌─ [DUPLICATE] Cloning ────────────────────────"
                    echo "   URL    : ${params.DUPLICATE_REPO_URL}"
                    echo "   Branch : ${params.DUPLICATE_BRANCH}"
                    git clone --branch ${params.DUPLICATE_BRANCH} ${params.DUPLICATE_REPO_URL} duplicate
                    echo "   Total commits : \$(cd duplicate && git rev-list --count HEAD)"
                    echo "   Total files   : \$(cd duplicate && git ls-files | wc -l | tr -d ' ')"
                    echo "└──────────────────────────────────────────────"
                """
            }
        }

        // ══════════════════════════════════════════
        // STAGE 2 — GITLEAKS: ORIGINAL REPO
        // ══════════════════════════════════════════
        stage('Gitleaks — Original Repo') {
            when {
                anyOf {
                    expression { return params.ORIGINAL_BRANCH_SCAN }
                    expression { return params.ORIGINAL_FULL_HISTORY }
                }
            }
            steps {
                script {

                    // ── ORIGINAL BRANCH SCAN ──────────────────────
                    if (params.ORIGINAL_BRANCH_SCAN) {
                        sh """
                            echo ""
                            echo "╔══════════════════════════════════════════════╗"
                            echo "║  GITLEAKS ▸ ORIGINAL ▸ BRANCH SCAN          ║"
                            echo "║  Branch : ${params.ORIGINAL_BRANCH}          "
                            echo "╚══════════════════════════════════════════════╝"
                            echo ""
                            echo "  Scanning commits reachable from origin/${params.ORIGINAL_BRANCH} ..."
                            echo "  Command: gitleaks detect --source=. --log-opts=origin/${params.ORIGINAL_BRANCH} --verbose"
                            echo ""
                            cd original
                            gitleaks detect \\
                                --source=. \\
                                --log-opts="origin/${params.ORIGINAL_BRANCH}" \\
                                --verbose
                            EXIT_CODE=\$?
                            if [ \$EXIT_CODE -eq 0 ]; then
                                echo ""
                                echo "  [RESULT] ✅ No secrets found in ORIGINAL BRANCH SCAN"
                            else
                                echo ""
                                echo "  [RESULT] ⚠️  Secrets/findings detected in ORIGINAL BRANCH SCAN (exit=\$EXIT_CODE)"
                            fi
                        """ // gitleaks non-zero = findings found; we capture manually above
                    }

                    // ── ORIGINAL FULL HISTORY SCAN ────────────────
                    if (params.ORIGINAL_FULL_HISTORY) {
                        sh """
                            echo ""
                            echo "╔══════════════════════════════════════════════╗"
                            echo "║  GITLEAKS ▸ ORIGINAL ▸ FULL HISTORY SCAN    ║"
                            echo "║  Scanning ALL commits across ALL branches    ║"
                            echo "╚══════════════════════════════════════════════╝"
                            echo ""
                            echo "  Command: gitleaks detect --source=. --log-opts=--all --verbose"
                            echo "  Commits to scan: \$(cd original && git rev-list --count --all) (all branches)"
                            echo ""
                            cd original
                            gitleaks detect \\
                                --source=. \\
                                --log-opts="--all" \\
                                --verbose
                            EXIT_CODE=\$?
                            if [ \$EXIT_CODE -eq 0 ]; then
                                echo ""
                                echo "  [RESULT] ✅ No secrets found in ORIGINAL FULL HISTORY SCAN"
                            else
                                echo ""
                                echo "  [RESULT] ⚠️  Secrets/findings detected in ORIGINAL FULL HISTORY SCAN (exit=\$EXIT_CODE)"
                            fi
                        """
                    }
                }
            }
        }

        // ══════════════════════════════════════════
        // STAGE 3 — GITLEAKS: DUPLICATE REPO
        // ══════════════════════════════════════════
        stage('Gitleaks — Duplicate Repo') {
            when {
                anyOf {
                    expression { return params.DUPLICATE_BRANCH_SCAN }
                    expression { return params.DUPLICATE_FULL_HISTORY }
                }
            }
            steps {
                script {

                    // ── DUPLICATE BRANCH SCAN ─────────────────────
                    if (params.DUPLICATE_BRANCH_SCAN) {
                        sh """
                            echo ""
                            echo "╔══════════════════════════════════════════════╗"
                            echo "║  GITLEAKS ▸ DUPLICATE ▸ BRANCH SCAN         ║"
                            echo "║  Branch : ${params.DUPLICATE_BRANCH}         "
                            echo "╚══════════════════════════════════════════════╝"
                            echo ""
                            echo "  Scanning commits reachable from origin/${params.DUPLICATE_BRANCH} ..."
                            echo "  Command: gitleaks detect --source=. --log-opts=origin/${params.DUPLICATE_BRANCH} --verbose"
                            echo ""
                            cd duplicate
                            gitleaks detect \\
                                --source=. \\
                                --log-opts="origin/${params.DUPLICATE_BRANCH}" \\
                                --verbose
                            EXIT_CODE=\$?
                            if [ \$EXIT_CODE -eq 0 ]; then
                                echo ""
                                echo "  [RESULT] ✅ No secrets found in DUPLICATE BRANCH SCAN"
                            else
                                echo ""
                                echo "  [RESULT] ⚠️  Secrets/findings detected in DUPLICATE BRANCH SCAN (exit=\$EXIT_CODE)"
                            fi
                        """
                    }

                    // ── DUPLICATE FULL HISTORY SCAN ───────────────
                    if (params.DUPLICATE_FULL_HISTORY) {
                        sh """
                            echo ""
                            echo "╔══════════════════════════════════════════════╗"
                            echo "║  GITLEAKS ▸ DUPLICATE ▸ FULL HISTORY SCAN   ║"
                            echo "║  Scanning ALL commits across ALL branches    ║"
                            echo "╚══════════════════════════════════════════════╝"
                            echo ""
                            echo "  Command: gitleaks detect --source=. --log-opts=--all --verbose"
                            echo "  Commits to scan: \$(cd duplicate && git rev-list --count --all) (all branches)"
                            echo ""
                            cd duplicate
                            gitleaks detect \\
                                --source=. \\
                                --log-opts="--all" \\
                                --verbose
                            EXIT_CODE=\$?
                            if [ \$EXIT_CODE -eq 0 ]; then
                                echo ""
                                echo "  [RESULT] ✅ No secrets found in DUPLICATE FULL HISTORY SCAN"
                            else
                                echo ""
                                echo "  [RESULT] ⚠️  Secrets/findings detected in DUPLICATE FULL HISTORY SCAN (exit=\$EXIT_CODE)"
                            fi
                        """
                    }
                }
            }
        }

        // ══════════════════════════════════════════
        // STAGE 4 — REPOSITORY COMPARISON
        // ══════════════════════════════════════════
        stage('Repository Comparison') {
            when {
                anyOf {
                    expression { return params.BRANCH_COMPARE }
                    expression { return params.ALL_BRANCH_COMPARE }
                }
            }
            steps {
                script {

                    // ── FILE DIFFERENCE (BRANCH COMPARE) ─────────
                    if (params.BRANCH_COMPARE) {
                        sh '''#!/bin/bash
                            echo ""
                            echo "╔══════════════════════════════════════════════╗"
                            echo "║  COMPARE ▸ FILE DIFFERENCE (BRANCH)         ║"
                            echo "╚══════════════════════════════════════════════╝"
                            echo ""

                            ORIG_COUNT=$(cd original && git ls-files | wc -l | tr -d ' ')
                            DUP_COUNT=$(cd duplicate && git ls-files | wc -l | tr -d ' ')

                            echo "  [ORIGINAL]  Total tracked files : $ORIG_COUNT"
                            echo "  [DUPLICATE] Total tracked files : $DUP_COUNT"
                            echo ""

                            ORIG_ONLY=$(diff \
                                <(cd original  && git ls-files | sort) \
                                <(cd duplicate && git ls-files | sort) \
                                | grep "^<" | sed 's/^< //' )

                            DUP_ONLY=$(diff \
                                <(cd original  && git ls-files | sort) \
                                <(cd duplicate && git ls-files | sort) \
                                | grep "^>" | sed 's/^> //' )

                            if [ -n "$ORIG_ONLY" ]; then
                                echo "  ─── Files ONLY in ORIGINAL ────────────────"
                                echo "$ORIG_ONLY" | while read -r f; do
                                    echo "    [ORIGINAL-ONLY]  $f"
                                done
                            else
                                echo "  [ORIGINAL-ONLY]  (none)"
                            fi

                            echo ""

                            if [ -n "$DUP_ONLY" ]; then
                                echo "  ─── Files ONLY in DUPLICATE ───────────────"
                                echo "$DUP_ONLY" | while read -r f; do
                                    echo "    [DUPLICATE-ONLY] $f"
                                done
                            else
                                echo "  [DUPLICATE-ONLY] (none)"
                            fi

                            ORIG_ONLY_COUNT=$(echo "$ORIG_ONLY" | grep -c . || true)
                            DUP_ONLY_COUNT=$(echo "$DUP_ONLY"  | grep -c . || true)

                            echo ""
                            echo "  ─── Summary ───────────────────────────────"
                            echo "    Files only in ORIGINAL  : $ORIG_ONLY_COUNT"
                            echo "    Files only in DUPLICATE : $DUP_ONLY_COUNT"
                            echo "    Files matching (shared) : $((ORIG_COUNT < DUP_COUNT ? ORIG_COUNT - ORIG_ONLY_COUNT : DUP_COUNT - DUP_ONLY_COUNT))"
                        '''
                    }

                    // ── BRANCH DIFFERENCE (ALL BRANCHES) ─────────
                    if (params.ALL_BRANCH_COMPARE) {
                        sh '''#!/bin/bash
                            echo ""
                            echo "╔══════════════════════════════════════════════╗"
                            echo "║  COMPARE ▸ BRANCH DIFFERENCE (ALL BRANCHES) ║"
                            echo "╚══════════════════════════════════════════════╝"
                            echo ""

                            ORIG_BRANCHES=$(cd original  && git branch -r | grep -v 'HEAD' | sort)
                            DUP_BRANCHES=$(cd duplicate  && git branch -r | grep -v 'HEAD' | sort)

                            echo "  [ORIGINAL]  Remote branches:"
                            echo "$ORIG_BRANCHES" | while read -r b; do echo "    $b"; done

                            echo ""
                            echo "  [DUPLICATE] Remote branches:"
                            echo "$DUP_BRANCHES"  | while read -r b; do echo "    $b"; done

                            echo ""
                            echo "  ─── Branches ONLY in ORIGINAL ─────────────"
                            diff <(echo "$ORIG_BRANCHES") <(echo "$DUP_BRANCHES") \
                                | grep "^<" | sed 's/^< /    [ORIGINAL-ONLY]  /' || echo "    (none)"

                            echo ""
                            echo "  ─── Branches ONLY in DUPLICATE ────────────"
                            diff <(echo "$ORIG_BRANCHES") <(echo "$DUP_BRANCHES") \
                                | grep "^>" | sed 's/^> /    [DUPLICATE-ONLY] /' || echo "    (none)"
                        '''
                    }
                }
            }
        }
    }

    // ─────────────────────────────────────────────
    // POST — CONSOLE SUMMARY + CLEANUP
    // ─────────────────────────────────────────────
    post {
        always {
            sh '''
                echo ""
                echo "╔══════════════════════════════════════════════╗"
                echo "║              PIPELINE SUMMARY                ║"
                echo "╠══════════════════════════════════════════════╣"
                echo "║  OUTPUT MODE  : CONSOLE_ONLY                 ║"
                echo "║  JSON Reports : NOT GENERATED                ║"
                echo "║  Artifacts    : NOT ARCHIVED                 ║"
                echo "║  Output Files : NOT SAVED                    ║"
                echo "╚══════════════════════════════════════════════╝"
                echo ""
                rm -rf original duplicate
                echo "[CLEANUP] Clone directories removed."
            '''
        }
        success {
            echo "[STATUS] PIPELINE SUCCEEDED — All enabled stages completed."
        }
        unstable {
            echo "[STATUS] PIPELINE UNSTABLE — Some stages reported warnings."
        }
        failure {
            echo "[STATUS] PIPELINE FAILED — Review console output above for errors."
        }
    }
}
