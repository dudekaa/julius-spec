pipeline {
    agent any

    options {
        buildDiscarder logRotator(numToKeepStr: '20')
        disableConcurrentBuilds()
        timestamps()
        timeout(time: 60, unit: 'MINUTES')
    }

    triggers {
        // Run between 10:00 and 10:59 AM in the specified timezone
        cron("TZ=Europe/Prague\nH 10 * * *")
    }

    environment {
        // Configuration
        UPSTREAM_GIT_URL        = 'https://github.com/bvschaik/julius.git'
        PACKAGING_REPO_URL      = 'https://nostovo.arnostdudek.cz:8085/nost23/julius-spec.git'
        PACKAGE_NAME            = 'julius'

        // Image with copr-cli
        REGISTRY                = 'nostovo.arnostdudek.cz:32769'
        IMAGE_NAME              = 'copr-builder'

        // Credentials
        COPR_CONFIG_ID          = 'copr-auth'      // ID of secret file credential
        DOCKER_CRED_ID          = 'nexus-jenkins'  // ID of username/password credential for image pulls
        GIT_CRED_ID             = 'forgejo-token'  // ID of username/password credential for pushing
    }

    stages {
        stage('Check Versions') {
            steps {
                script {
                    // Get Latest Upstream Tag (Remote)
                    // Note: git ls-remote --tags --sort=-v:refname returns tags sorted by version descending.
                    // We filter out ^{} (dereferenced tags) and grab the first result.
                    // Result format: <hash>\trefs/tags/v1.8.0  →  we extract just the tag name.
                    def remoteTag = sh(returnStdout: true, script: """
                        git ls-remote --tags --sort=-v:refname ${UPSTREAM_GIT_URL} \
                        | grep -v '\\^{}' \
                        | head -n 1 \
                        | awk '{print \$2}' \
                        | sed 's|refs/tags/||'
                    """).trim()
                    echo "Upstream Tag: ${remoteTag}"

                    // Strip leading 'v' to get the version number (e.g., v1.8.0 -> 1.8.0)
                    def remoteVersion = remoteTag.replaceFirst(/^v/, '')
                    echo "Upstream Version: ${remoteVersion}"

                    // Get Local Version (from Spec file)
                    // Note: We extract the value defined in Version:
                    def localVersion = sh(returnStdout: true, script: "grep '^Version:' ${PACKAGE_NAME}.spec | awk '{print \$2}'").trim()
                    echo "Local Spec Version: ${localVersion}"

                    // Compare
                    if (remoteVersion == localVersion) {
                        echo "No changes detected. Skipping build."
                        currentBuild.result = 'SUCCESS'
                        env.UPDATE_NEEDED = 'false'
                        env.NEW_VERSION = localVersion
                    } else {
                        echo "New version detected (${localVersion} -> ${remoteVersion})! Preparing update."
                        env.UPDATE_NEEDED = 'true'
                        env.NEW_VERSION = remoteVersion
                        env.NEW_TAG = remoteTag
                    }
                }
            }
        }

        stage('Check Release Bump') {
            when {
                beforeAgent true
                not {
                    environment name: 'UPDATE_NEEDED', value: 'true'
                }
            }
            agent {
                docker {
                    alwaysPull true
                    image "${REGISTRY}/${IMAGE_NAME}"
                    registryCredentialsId DOCKER_CRED_ID
                    registryUrl "https://${REGISTRY}"
                    reuseNode true
                }
            }
            steps {
                script {
                    // Get Local Release (from Spec file)
                    def localRelease = sh(returnStdout: true, script: "grep '^Release:' ${PACKAGE_NAME}.spec | awk '{print \$2}' | sed 's/%{?dist}//'").trim()
                    echo "Local Spec Release: ${localRelease}"

                    // Get COPR Release (latest build) using jq
                    def coprRelease = ''
                    withCredentials([file(credentialsId: COPR_CONFIG_ID, variable: 'COPR_CONFIG_FILE')]) {
                        coprRelease = sh(returnStdout: true, script: """
                            copr-cli --config \${COPR_CONFIG_FILE} get-package ${PACKAGE_NAME} --name ${PACKAGE_NAME} --with-latest-build --output-format json \
                            | jq -r '.latest_build.source_package.version' \
                            | cut -d'-' -f2
                        """).trim()
                    }
                    echo "COPR Release: ${coprRelease}"

                    // Compare releases (simple numeric comparison for format like "1" or "2")
                    if (coprRelease && localRelease.toInteger() > coprRelease.toInteger()) {
                        echo "Local release (${localRelease}) is higher than COPR release (${coprRelease}). Triggering build."
                        env.RELEASE_BUMP_ONLY = 'true'

                        // Set trigger for next steps
                        env.UPDATE_NEEDED = 'true'
                    } else {
                        echo "No release bump detected. Local: ${localRelease}, COPR: ${coprRelease}"
                    }
                }
            }
        }

        stage('Lint') {
            when {
                beforeAgent true
                environment name: 'UPDATE_NEEDED', value: 'true'
            }
            // Run inside the container where rpmdevtools/copr-cli are installed
            agent {
                docker {
                    alwaysPull true
                    image "${REGISTRY}/${IMAGE_NAME}"
                    registryCredentialsId DOCKER_CRED_ID
                    registryUrl "https://${REGISTRY}"
                    reuseNode true
                }
            }
            steps {
                sh "rpmlint ${PACKAGE_NAME}.spec"
            }
        }

        stage('Update Spec & Push') {
            when {
                beforeAgent true
                environment name: 'UPDATE_NEEDED', value: 'true'
            }
            agent {
                docker {
                    alwaysPull true
                    image "${REGISTRY}/${IMAGE_NAME}"
                    registryCredentialsId DOCKER_CRED_ID
                    registryUrl "https://${REGISTRY}"
                    args '--add-host nostovo.arnostdudek.cz:192.168.1.2'
                    reuseNode true
                }
            }
            steps {
                script {
                    if (env.RELEASE_BUMP_ONLY == 'true') {
                        // Just bump the release number (e.g., 1 -> 2)
                        sh """
                            rpmdev-bumpspec \
                            --comment "Minor spec file updates" \
                            --userstring "Jenkins <jenkins@nostovo>" \
                            ${PACKAGE_NAME}.spec
                        """
                    } else {
                        // Atomic Version Update:
                        // Sets Version to NEW_VERSION, resets Release to 1, and adds changelog
                        sh """
                            rpmdev-bumpspec \
                            --new "${env.NEW_VERSION}" \
                            --comment "Automated update to upstream version ${env.NEW_VERSION}" \
                            --userstring "Jenkins <jenkins@nostovo>" \
                            ${PACKAGE_NAME}.spec
                        """
                    }

                    // Debug: Use rpmspec to query the fully expanded Release field
                    sh "rpmspec -q --qf 'Version: %{VERSION}\n' ${PACKAGE_NAME}.spec"
                    sh "rpmspec -q --qf 'Release: %{RELEASE}\n' ${PACKAGE_NAME}.spec"

                    // Debug: Show what happened with changelog
                    sh "grep -A 5 '%changelog' ${PACKAGE_NAME}.spec"

                    // Configure Git Identity
                    sh 'git config user.email "jenkins@nostovo"'
                    sh 'git config user.name "Jenkins"'

                    // Commit changes locally
                    sh "git add ${PACKAGE_NAME}.spec"
                    sh "git commit -m 'chore: Auto-update to upstream version ${NEW_VERSION}'"

                    // PUSH via HTTPS (Dynamic URL Injection)
                    // We reuse the existing 'origin' URL but inject credentials
                    withCredentials([usernamePassword(credentialsId: GIT_CRED_ID, usernameVariable: 'GIT_USER', passwordVariable: 'GIT_TOKEN')]) {
                        sh '''
                            # Get the current remote URL (e.g., https://domain.com/repo.git)
                            ORIGIN_URL=$(git remote get-url origin)

                            # Strip the protocol (https://) to get just the domain/path
                            # Result: domain.com/repo.git
                            URL_WITHOUT_PROTO=${ORIGIN_URL#*://}

                            # Push using the constructed URL with auth
                            # Structure: https://<user>:<token>@<domain/path>
                            git push "https://${GIT_USER}:${GIT_TOKEN}@${URL_WITHOUT_PROTO}" HEAD:main
                        '''
                    }
                }
            }
        }

        stage('Trigger COPR Build') {
            when {
                beforeAgent true
                environment name: 'UPDATE_NEEDED', value: 'true'
            }
            agent {
                docker {
                    alwaysPull true
                    image "${REGISTRY}/${IMAGE_NAME}"
                    registryCredentialsId DOCKER_CRED_ID
                    registryUrl "https://${REGISTRY}"
                    reuseNode true
                }
            }
            steps {
                withCredentials([file(credentialsId: COPR_CONFIG_ID, variable: 'COPR_CONFIG_FILE')]) {
                    // Trigger build and WAIT for result (it pulls what we just pushed)
                    // NOTE: use single-quotes around sensitive variables. https://jenkins.io/redirect/groovy-string-interpolation
                    sh 'copr-cli --config ${COPR_CONFIG_FILE} buildscm ${PACKAGE_NAME} --clone-url ${PACKAGING_REPO_URL} --spec ${PACKAGE_NAME}.spec'
                }
            }
        }
    }

    post {
        failure {
            // TODO maybe use emailext plugin
            mail to: 'your-email@nostovo.arnostdudek.cz',
                 subject: "❌ Build Failed: ${currentBuild.fullDisplayName}",
                 body: "The build failed. Please check the logs here: ${env.BUILD_URL}"
        }
        fixed {
            mail to: 'your-email@nostovo.arnostdudek.cz',
                 subject: "✅ Build Fixed: ${currentBuild.fullDisplayName}",
                 body: "Good news! The build is back to normal. See: ${env.BUILD_URL}"
        }
    }
}