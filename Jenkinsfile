
pipeline {
    agent any

    triggers {
        githubPush()
        pollSCM('H/2 * * * *')
    }

    options {
        skipDefaultCheckout(true)
        disableConcurrentBuilds()
        timestamps()
    }

    environment {
        IMAGE_NAME = 'student-internship-tracker'
        K8S_DEPLOYMENT = 'student-tracker'
        K8S_CONTAINER = 'student-tracker'
        K8S_NAMESPACE = 'default'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                echo 'Source code checked out successfully.'
            }
        }

        stage('Install Dependencies and Test') {
            steps {
                bat 'python --version'
                bat 'python -m pip install -r requirements.txt'
                bat 'python -m pytest -v'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    env.IMAGE_TAG = "${env.BUILD_NUMBER}"
                    env.FULL_IMAGE = "${env.DOCKERHUB_USERNAME}/${env.IMAGE_NAME}:${env.IMAGE_TAG}"
                }

                bat 'docker build -t %FULL_IMAGE% -t %DOCKERHUB_USERNAME%/%IMAGE_NAME%:latest .'
            }
        }

        stage('Push Docker Image') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-creds',
                        usernameVariable: 'preezypanda0711',
                        passwordVariable: 'Asdfghjkl'
                    )
                ]) {
                    bat '''
                        @echo off
                        echo %DOCKERHUB_PASSWORD%| docker login --username %DOCKERHUB_USERNAME% --password-stdin
                        if errorlevel 1 exit /b 1

                        docker push %FULL_IMAGE%
                        if errorlevel 1 exit /b 1

                        docker push %DOCKERHUB_USERNAME%/%IMAGE_NAME%:latest
                        if errorlevel 1 exit /b 1

                        docker logout
                    '''
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                bat 'kubectl config current-context'
                bat 'kubectl apply -f k8s/'

                bat '''
                    kubectl set image deployment/%K8S_DEPLOYMENT% %K8S_CONTAINER%=%FULL_IMAGE% -n %K8S_NAMESPACE%
                    if errorlevel 1 exit /b 1
                '''

                bat 'kubectl rollout status deployment/%K8S_DEPLOYMENT% -n %K8S_NAMESPACE% --timeout=180s'
                bat 'kubectl get pods -l app=student-tracker -n %K8S_NAMESPACE%'
            }
        }
    }

    post {
        success {
            echo 'CI/CD completed: tests passed, image pushed, application deployed.'
        }
        failure {
            echo 'CI/CD failed. Check the stage logs before retrying.'
        }
        always {
            echo 'Pipeline execution finished.'
        }
    }
}
