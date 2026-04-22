pipelineJob('gitleaks-multirepo-scan') {
    description('Run gitleaks scans and repository comparisons for original and duplicate GitHub repositories.')

    definition {
        cpsScm {
            scm {
                git {
                    remote {
                        url('https://github.com/narayanareddy11/gitleaks-test.git')
                    }
                    branch('*/main')
                }
            }
            scriptPath('Jenkinsfile')
            lightweight(true)
        }
    }
}
