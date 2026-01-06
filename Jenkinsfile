pipeline {
    agent any

    options {
        disableConcurrentBuilds abortPrevious: true
        timestamps()
        timeout(10)
    }

    triggers {
        pollSCM '''TZ=Europe/Prague
            H/5 * * * *'''
    }

    environment {
        COPR_CONFIG_FILE = credentials('copr-auth')
        REGISTRY = 'nostovo.arnostdudek.cz:32769'
        IMAGE_NAME = 'copr-builder'
        IMAGE_TAG = "${REGISTRY}/${IMAGE_NAME}"
    }

    parameters {
      gitParameter type: 'PT_TAG',
         name: 'BUILD_TAG',
         defaultValue: 'v1.8.0-1',
         description: 'Which tag to build',
         selectedValue: 'TOP',
         sortMode: 'DESCENDING_SMART'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scmGit(
                    branches: [[name: params.BUILD_TAG]],
                    browser: github('https://github.com/dudekaa/julius-spec'),
                    extensions: [],
                    userRemoteConfigs: [
                        [
                            url: 'https://github.com/dudekaa/julius-spec.git'
                        ]
                    ]
                )
            }
        }

        stage('Lint') {
            agent {
                docker {
                    alwaysPull true
                    image "${IMAGE_TAG}"
                    registryCredentialsId 'nexus-jenkins'
                    registryUrl "https://${REGISTRY}"
                }
            }
            steps {
                sh 'rpmlint julius.spec'
            }
        }

        stage('Build') {
            agent {
                docker {
                    alwaysPull true
                    image "${IMAGE_TAG}"
                    registryCredentialsId 'nexus-jenkins'
                    registryUrl "https://${REGISTRY}"
                }
            }
            // trigger build in COPR infrastructure
            steps {
                sh 'copr-cli --config ' + COPR_CONFIG_FILE + ' buildscm julius --clone-url https://github.com/dudekaa/julius-spec.git --spec julius.spec --commit ' + params.BUILD_TAG
            }
        }
    }
}