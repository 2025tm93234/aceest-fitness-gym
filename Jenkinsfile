pipeline {
    agent any

    triggers {
        pollSCM('H/5 * * * *')
    }

    parameters {
        choice(name: 'APP_VERSION',
               choices: ['3.2.4', '3.1.2', '2.2.4', '2.2.1', '2.0.1', '1.1.2', '1.1', '1.0'],
               description: 'ACEest release to build, test, publish and deploy')
        booleanParam(name: 'PUSH_IMAGE', defaultValue: true,
                     description: 'Push the image to Docker Hub')
        booleanParam(name: 'DEPLOY', defaultValue: true,
                     description: 'Roll the Minikube cluster to this release (needs PUSH_IMAGE)')
        booleanParam(name: 'BUILD_ALL_VERSIONS', defaultValue: false,
                     description: 'Build and push an image for every release (and alias tags)')
    }

    environment {
        VENV           = "venv"
        // Jenkins credentials: "dockerhub-creds" (username + token) and "sonar-token" (secret text)
        DOCKERHUB      = credentials('dockerhub-creds')
        IMAGE_REPO     = "${DOCKERHUB_USR}/aceest-fitness"
        SONAR_HOST_URL = "http://localhost:9000"
    }

    stages {
        stage('Checkout') {
            steps {
                deleteDir()
                checkout scm
            }
        }

        stage('Setup Environment') {
            steps {
                sh '''
                    python3 -m venv ${VENV}
                    . ${VENV}/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Lint') {
            steps {
                sh '''
                    . ${VENV}/bin/activate
                    python -m flake8 aceest app.py tests/
                '''
            }
        }

        stage('Unit Tests') {
            steps {
                sh '''
                    . ${VENV}/bin/activate
                    python -m pytest -v --cov=aceest --cov-report=term --cov-report=xml --junitxml=report.xml
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'report.xml'
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withCredentials([string(credentialsId: 'sonar-token', variable: 'SONAR_TOKEN')]) {
                    sh '''
                        docker run --rm --network host -u "$(id -u):$(id -g)" \
                            -e SONAR_HOST_URL="$SONAR_HOST_URL" -e SONAR_TOKEN="$SONAR_TOKEN" \
                            -e SONAR_USER_HOME=/tmp/.sonar \
                            -v "$PWD:/usr/src" sonarsource/sonar-scanner-cli \
                            -Dsonar.working.directory=/usr/src/.scannerwork \
                            -Dsonar.projectVersion="$APP_VERSION"
                    '''
                }
            }
        }

        stage('Quality Gate') {
            steps {
                withCredentials([string(credentialsId: 'sonar-token', variable: 'SONAR_TOKEN')]) {
                    sh 'scripts/sonar_quality_gate.sh'
                }
            }
        }

        stage('Docker Build') {
            steps {
                sh '''
                    docker build --build-arg APP_VERSION=${APP_VERSION} \
                        -t ${IMAGE_REPO}:${APP_VERSION} -t ${IMAGE_REPO}:build-${BUILD_NUMBER} .
                '''
            }
        }

        stage('Container Smoke Test') {
            steps {
                sh 'scripts/smoke_test.sh ${IMAGE_REPO}:${APP_VERSION} ${APP_VERSION}'
            }
        }

        stage('Push to Docker Hub') {
            when { expression { params.PUSH_IMAGE } }
            steps {
                sh '''
                    echo "$DOCKERHUB_PSW" | docker login -u "$DOCKERHUB_USR" --password-stdin
                    docker push ${IMAGE_REPO}:${APP_VERSION}
                    docker push ${IMAGE_REPO}:build-${BUILD_NUMBER}
                    if [ "${APP_VERSION}" = "3.2.4" ]; then
                        docker tag ${IMAGE_REPO}:3.2.4 ${IMAGE_REPO}:latest
                        docker push ${IMAGE_REPO}:latest
                    fi
                    docker logout
                '''
            }
        }

        stage('Publish All Versions') {
            when { expression { params.BUILD_ALL_VERSIONS } }
            steps {
                sh '''
                    echo "$DOCKERHUB_PSW" | docker login -u "$DOCKERHUB_USR" --password-stdin
                    scripts/build_push_all.sh
                    docker logout
                '''
            }
        }

        stage('Deploy to Minikube') {
            when { expression { params.DEPLOY && params.PUSH_IMAGE } }
            steps {
                sh 'scripts/deploy_rolling.sh ${APP_VERSION}'
            }
        }
    }

    post {
        always {
            sh 'docker rmi ${IMAGE_REPO}:build-${BUILD_NUMBER} || true'
            echo "Build #${BUILD_NUMBER} (release ${APP_VERSION}) finished with status: ${currentBuild.currentResult}"
        }
    }
}
