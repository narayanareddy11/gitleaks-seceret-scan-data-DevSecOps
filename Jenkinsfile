pipeline {
    agent {
        kubernetes {
            label 'gitleaks-scanner'
            yaml '''
apiVersion: v1
kind: Pod
spec:
  serviceAccountName: jenkins
  containers:
  - name: scanner
    image: python:3.11-slim
    command: ["sleep", "infinity"]
    tty: true
    env:
    - name: PYTHONUNBUFFERED
      value: "1"
    resources:
      requests:
        cpu: "500m"
        memory: "512Mi"
      limits:
        cpu: "1"
        memory: "1Gi"
'''
            defaultContainer 'scanner'
        }
    }

    parameters {
        booleanParam(name: 'ENABLE_ORIGINAL_REPO',  defaultValue: true,  description: 'Clone and use the original repository')
        booleanParam(name: 'ENABLE_DUPLICATE_REPO', defaultValue: true,  description: 'Clone and use the duplicate repository')

        string(name: 'ORIGINAL_REPO_URL', defaultValue: 'https://github.com/narayanareddy11/gitleaks-test-original', description: 'Original repository URL')
        string(name: 'ORIGINAL_BRANCH',   defaultValue: 'main', description: 'Original repository branch')
        string(name: 'DUPLICATE_REPO_URL', defaultValue: 'https://github.com/narayanareddy11/gitleaks-test-duplicate', description: 'Duplicate repository URL')
        string(name: 'DUPLICATE_BRANCH',   defaultValue: 'main', description: 'Duplicate repository branch')

        booleanParam(name: 'ORIGINAL_BRANCH_SCAN',   defaultValue: true,  description: '[GITLEAKS] Scan original selected branch')
        booleanParam(name: 'ORIGINAL_FULL_HISTORY',  defaultValue: false, description: '[GITLEAKS] Scan original full git history')
        booleanParam(name: 'DUPLICATE_BRANCH_SCAN',  defaultValue: true,  description: '[GITLEAKS] Scan duplicate selected branch')
        booleanParam(name: 'DUPLICATE_FULL_HISTORY', defaultValue: false, description: '[GITLEAKS] Scan duplicate full git history')

        booleanParam(name: 'COMPARE_TRACKED_FILES',  defaultValue: true,  description: '[COMPARE] Compare tracked file lists between original and duplicate')
        booleanParam(name: 'COMPARE_FILE_CHANGES',   defaultValue: true,  description: '[COMPARE] Compare new, missing, and modified files between original and duplicate')
        booleanParam(name: 'SHOW_MODIFIED_DIFFS',    defaultValue: false, description: '[COMPARE] Print diff preview for modified text files')
        booleanParam(name: 'COMPARE_REMOTE_BRANCHES', defaultValue: false, description: '[COMPARE] Compare all remote branches between original and duplicate')

        string(name: 'GITLEAKS_VERSION', defaultValue: '8.24.2', description: 'Gitleaks version to install inside the scanner pod')
    }

    stages {
        stage('Prepare Tools') {
            steps {
                sh '''
                    set -eu

                    apt-get update
                    apt-get install -y --no-install-recommends git curl ca-certificates tar gzip

                    ARCH="$(uname -m)"
                    case "$ARCH" in
                      x86_64|amd64) GITLEAKS_ARCH="x64" ;;
                      aarch64|arm64) GITLEAKS_ARCH="arm64" ;;
                      *)
                        echo "[ERROR] Unsupported architecture: $ARCH"
                        exit 1
                        ;;
                    esac

                    TMP_DIR="$(mktemp -d)"
                    curl -fsSL -o "$TMP_DIR/gitleaks.tar.gz" \
                      "https://github.com/gitleaks/gitleaks/releases/download/v${GITLEAKS_VERSION}/gitleaks_${GITLEAKS_VERSION}_linux_${GITLEAKS_ARCH}.tar.gz"
                    tar -xzf "$TMP_DIR/gitleaks.tar.gz" -C "$TMP_DIR"
                    install "$TMP_DIR/gitleaks" /usr/local/bin/gitleaks

                    git --version
                    gitleaks version
                '''
            }
        }

        stage('Clone Repositories') {
            steps {
                script {
                    def originalFlag = params.ENABLE_ORIGINAL_REPO ? '--original-enabled' : ''
                    def duplicateFlag = params.ENABLE_DUPLICATE_REPO ? '--duplicate-enabled' : ''

                    sh """
                        python3 -u scripts/clone_repos.py \\
                            ${originalFlag} \\
                            ${duplicateFlag} \\
                            --original-url "${params.ORIGINAL_REPO_URL}" \\
                            --original-branch "${params.ORIGINAL_BRANCH}" \\
                            --duplicate-url "${params.DUPLICATE_REPO_URL}" \\
                            --duplicate-branch "${params.DUPLICATE_BRANCH}"
                    """
                }
            }
        }

        stage('Gitleaks - Original Repo') {
            when {
                expression {
                    return params.ENABLE_ORIGINAL_REPO &&
                        (params.ORIGINAL_BRANCH_SCAN || params.ORIGINAL_FULL_HISTORY)
                }
            }
            steps {
                script {
                    if (params.ORIGINAL_BRANCH_SCAN) {
                        sh """
                            python3 -u scripts/gitleaks_scan.py \\
                                --repo-dir original \\
                                --label ORIGINAL \\
                                --mode branch \\
                                --branch "${params.ORIGINAL_BRANCH}"
                        """
                    }
                    if (params.ORIGINAL_FULL_HISTORY) {
                        sh '''
                            python3 -u scripts/gitleaks_scan.py \
                                --repo-dir original \
                                --label ORIGINAL \
                                --mode full-history
                        '''
                    }
                }
            }
        }

        stage('Gitleaks - Duplicate Repo') {
            when {
                expression {
                    return params.ENABLE_DUPLICATE_REPO &&
                        (params.DUPLICATE_BRANCH_SCAN || params.DUPLICATE_FULL_HISTORY)
                }
            }
            steps {
                script {
                    if (params.DUPLICATE_BRANCH_SCAN) {
                        sh """
                            python3 -u scripts/gitleaks_scan.py \\
                                --repo-dir duplicate \\
                                --label DUPLICATE \\
                                --mode branch \\
                                --branch "${params.DUPLICATE_BRANCH}"
                        """
                    }
                    if (params.DUPLICATE_FULL_HISTORY) {
                        sh '''
                            python3 -u scripts/gitleaks_scan.py \
                                --repo-dir duplicate \
                                --label DUPLICATE \
                                --mode full-history
                        '''
                    }
                }
            }
        }

        stage('Repository Comparison') {
            when {
                expression {
                    return params.ENABLE_ORIGINAL_REPO &&
                        params.ENABLE_DUPLICATE_REPO &&
                        (
                            params.COMPARE_TRACKED_FILES ||
                            params.COMPARE_FILE_CHANGES ||
                            params.COMPARE_REMOTE_BRANCHES
                        )
                }
            }
            steps {
                script {
                    if (params.COMPARE_TRACKED_FILES) {
                        sh 'python3 -u scripts/compare_repos.py --mode branch'
                    }
                    if (params.COMPARE_FILE_CHANGES) {
                        def diffFlag = params.SHOW_MODIFIED_DIFFS ? '--show-diff' : ''
                        sh """
                            python3 -u scripts/compare_repos.py \\
                                --mode changes \\
                                ${diffFlag}
                        """
                    }
                    if (params.COMPARE_REMOTE_BRANCHES) {
                        sh 'python3 -u scripts/compare_repos.py --mode all-branches'
                    }
                }
            }
        }
    }

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
            echo "[STATUS] PIPELINE SUCCEEDED - All enabled stages completed."
        }
        unstable {
            echo "[STATUS] PIPELINE UNSTABLE - Some stages reported warnings."
        }
        failure {
            echo "[STATUS] PIPELINE FAILED - Review console output above for errors."
        }
    }
}
