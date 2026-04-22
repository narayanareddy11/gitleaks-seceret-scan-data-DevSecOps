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
                sh """
                    python3 -u scripts/clone_repos.py \\
                        --original-url    "${params.ORIGINAL_REPO_URL}" \\
                        --original-branch "${params.ORIGINAL_BRANCH}" \\
                        --duplicate-url   "${params.DUPLICATE_REPO_URL}" \\
                        --duplicate-branch "${params.DUPLICATE_BRANCH}"
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
                    if (params.ORIGINAL_BRANCH_SCAN) {
                        sh """
                            python3 -u scripts/gitleaks_scan.py \\
                                --repo-dir original \\
                                --label    ORIGINAL \\
                                --mode     branch \\
                                --branch   "${params.ORIGINAL_BRANCH}"
                        """
                    }
                    if (params.ORIGINAL_FULL_HISTORY) {
                        sh """
                            python3 -u scripts/gitleaks_scan.py \\
                                --repo-dir original \\
                                --label    ORIGINAL \\
                                --mode     full-history
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
                    if (params.DUPLICATE_BRANCH_SCAN) {
                        sh """
                            python3 -u scripts/gitleaks_scan.py \\
                                --repo-dir duplicate \\
                                --label    DUPLICATE \\
                                --mode     branch \\
                                --branch   "${params.DUPLICATE_BRANCH}"
                        """
                    }
                    if (params.DUPLICATE_FULL_HISTORY) {
                        sh """
                            python3 -u scripts/gitleaks_scan.py \\
                                --repo-dir duplicate \\
                                --label    DUPLICATE \\
                                --mode     full-history
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
                    if (params.BRANCH_COMPARE) {
                        sh "python3 -u scripts/compare_repos.py --mode branch"
                    }
                    if (params.ALL_BRANCH_COMPARE) {
                        sh "python3 -u scripts/compare_repos.py --mode all-branches"
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
