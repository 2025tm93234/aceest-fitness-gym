
pipeline {

    agent any



    triggers {

        pollSCM('H/5 * * * *')

    }



    environment {

        VENV = "venv"

    }



    stages {



        stage('Setup Environment') {

            steps {

                sh '''

                    python3 --version

                    docker --version



                    python3 -m venv ${VENV}



                    . ${VENV}/bin/activate



                    python -m pip install --upgrade pip

                    pip install -r requirements.txt

                '''

            }

        }



        stage('Lint') {

            steps {

                sh '''

                    . ${VENV}/bin/activate



                    python -m compileall -q app.py

                    flake8 app.py tests/

                '''

            }

        }



        stage('Unit Tests') {

            steps {

                sh '''

                    . ${VENV}/bin/activate



                    pytest -v --cov=app

                '''

            }

        }



        stage('Docker Build') {

            steps {

                sh '''

                    docker build -t aceest-fitness:${BUILD_NUMBER} .

                '''

            }

        }

    }



    post {

        always {

            echo "Build #${BUILD_NUMBER} finished with status: ${currentBuild.currentResult}"

        }

    }

}

