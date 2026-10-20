pipeline {
    agent any

    environment {
        IMAGE = 'sarthakh0607/todo-app'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                bat 'python -m venv venv'
                bat 'venv\\Scripts\\python -m pip install -r requirements.txt'
            }
        }

        stage('Build') {
            steps {
                bat 'venv\\Scripts\\python -m py_compile app.py'
            }
        }

        stage('Test') {
            steps {
                bat 'venv\\Scripts\\python -m pytest -v'
            }
        }

        stage('Docker Build') {
            steps {
                bat 'docker build -t %IMAGE%:%BUILD_NUMBER% -t %IMAGE%:latest .'
            }
        }

        stage('Docker Push') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds',
                                                  usernameVariable: 'DH_USER',
                                                  passwordVariable: 'DH_PASS')]) {
                    bat 'echo %DH_PASS%| docker login -u %DH_USER% --password-stdin'
                    bat 'docker push %IMAGE%:%BUILD_NUMBER%'
                    bat 'docker push %IMAGE%:latest'
                }
            }
        }

        stage('Deploy') {
            steps {
                bat 'docker rm -f todo || exit 0'
                bat 'docker run -d -p 5000:5000 --name todo %IMAGE%:latest'
            }
        }
    }

    post {
        success { echo 'Pipeline succeeded' }
        failure { echo 'Pipeline failed - deployment skipped' }
    }
}