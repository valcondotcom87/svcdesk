pipeline {
    agent any

    environment {
        REGISTRY = 'docker.io'
        IMAGE_NAME = 'your-registry/itsm-api'
        IMAGE_TAG = "${BUILD_NUMBER}"
        DOCKER_CREDENTIALS = credentials('docker-credentials')
        SONAR_TOKEN = credentials('sonarqube-token')
        DEPLOY_STAGING_HOST = credentials('staging-host')
        DEPLOY_PROD_HOST = credentials('prod-host')
    }

    options {
        timeout(time: 1, unit: 'HOURS')
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '20'))
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    env.GIT_COMMIT_SHORT = sh(
                        script: "git rev-parse --short HEAD",
                        returnStdout: true
                    ).trim()
                }
            }
        }

        stage('Build') {
            steps {
                dir('backend') {
                    sh '''
                        echo "Building Docker image..."
                        docker build -t ${IMAGE_NAME}:${IMAGE_TAG} \
                                    -t ${IMAGE_NAME}:latest \
                                    -t ${IMAGE_NAME}:${GIT_COMMIT_SHORT} .
                    '''
                }
            }
        }

        stage('Unit Tests') {
            steps {
                dir('backend') {
                    sh '''
                        echo "Running unit tests..."
                        docker run --rm \
                            -v $(pwd):/app \
                            -w /app \
                            python:3.11 /bin/bash -c "
                                pip install -q -r requirements.txt pytest pytest-cov pytest-django
                                cp .env.example .env
                                sed -i 's/DEBUG=True/DEBUG=False/' .env
                                pytest tests/ --cov=apps --cov-report=xml --junitxml=test-results.xml -v
                            "
                    '''
                }
            }
            post {
                always {
                    dir('backend') {
                        junit 'test-results.xml'
                        publishCoverage adapters: [coberturaAdapter('coverage.xml')]
                    }
                }
            }
        }

        stage('Code Quality Analysis') {
            steps {
                dir('backend') {
                    sh '''
                        echo "Running SonarQube analysis..."
                        docker run --rm \
                            -e SONAR_HOST_URL=http://sonarqube:9000 \
                            -e SONAR_LOGIN=${SONAR_TOKEN} \
                            -v $(pwd):/usr/src \
                            sonarsource/sonar-scanner-cli \
                            -Dsonar.projectKey=itsm-api \
                            -Dsonar.projectName="ITSM API" \
                            -Dsonar.sources=. \
                            -Dsonar.exclusions=tests/**,migrations/**,venv/**
                    '''
                }
            }
        }

        stage('Security Scan') {
            parallel {
                stage('Bandit') {
                    steps {
                        dir('backend') {
                            sh '''
                                echo "Running Bandit security scan..."
                                docker run --rm \
                                    -v $(pwd):/app \
                                    -w /app \
                                    python:3.11 /bin/bash -c "
                                        pip install -q bandit
                                        bandit -r apps -f json -o bandit-report.json || true
                                    "
                            '''
                        }
                    }
                }

                stage('Trivy') {
                    steps {
                        sh '''
                            echo "Running Trivy vulnerability scan..."
                            docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
                                aquasec/trivy:latest image \
                                --severity HIGH,CRITICAL \
                                --format json \
                                --output trivy-report.json \
                                ${IMAGE_NAME}:${IMAGE_TAG} || true
                        '''
                    }
                }
            }
        }

        stage('Push to Registry') {
            when {
                branch 'main'
            }
            steps {
                sh '''
                    echo "Pushing image to registry..."
                    echo ${DOCKER_CREDENTIALS_PSW} | docker login -u ${DOCKER_CREDENTIALS_USR} --password-stdin
                    docker push ${IMAGE_NAME}:${IMAGE_TAG}
                    docker push ${IMAGE_NAME}:latest
                    docker logout
                '''
            }
        }

        stage('Deploy to Staging') {
            when {
                branch 'develop'
            }
            environment {
                ENVIRONMENT = 'staging'
            }
            steps {
                dir('backend') {
                    sh '''
                        echo "Deploying to Staging..."
                        ssh -i ${DEPLOY_STAGING_HOST} ubuntu@staging.example.com << 'EOF'
                            cd /app
                            docker-compose pull
                            docker-compose up -d
                            docker-compose exec -T backend python manage.py migrate
                            sleep 10
                            docker-compose exec -T backend python manage.py collectstatic --noinput
                        EOF
                    '''
                }
            }
        }

        stage('Smoke Tests - Staging') {
            when {
                branch 'develop'
            }
            steps {
                sh '''
                    echo "Running smoke tests on staging..."
                    for i in {1..5}; do
                        if curl -f http://staging.example.com/health/ 2>/dev/null; then
                            echo "Staging health check passed"
                            break
                        fi
                        echo "Attempt $i: Waiting for service..."
                        sleep 10
                    done
                '''
            }
        }

        stage('Deploy to Production') {
            when {
                branch 'main'
            }
            environment {
                ENVIRONMENT = 'production'
            }
            input {
                message "Deploy to Production?"
                ok "Deploy"
                submitter "admin,devops"
            }
            steps {
                dir('backend') {
                    sh '''
                        echo "Deploying to Production..."
                        ssh -i ${DEPLOY_PROD_HOST} ubuntu@api.example.com << 'EOF'
                            cd /app
                            docker-compose -f docker-compose.yml -f docker-compose.prod.yml pull
                            docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
                            docker-compose -f docker-compose.yml -f docker-compose.prod.yml exec -T backend python manage.py migrate
                            sleep 10
                            docker-compose -f docker-compose.yml -f docker-compose.prod.yml exec -T backend python manage.py collectstatic --noinput
                        EOF
                    '''
                }
            }
        }

        stage('Smoke Tests - Production') {
            when {
                branch 'main'
            }
            steps {
                sh '''
                    echo "Running smoke tests on production..."
                    for i in {1..5}; do
                        if curl -f https://api.example.com/health/ 2>/dev/null; then
                            echo "Production health check passed"
                            break
                        fi
                        echo "Attempt $i: Waiting for service..."
                        sleep 10
                    done
                '''
            }
        }
    }

    post {
        always {
            dir('backend') {
                script {
                    // Archive reports
                    archiveArtifacts artifacts: 'test-results.xml,bandit-report.json,trivy-report.json', 
                                     allowEmptyArchive: true
                    
                    // Cleanup
                    sh '''
                        docker rmi ${IMAGE_NAME}:${IMAGE_TAG} || true
                        docker system prune -f || true
                    '''
                }
            }
        }

        success {
            echo "Pipeline succeeded!"
        }

        failure {
            echo "Pipeline failed!"
            // Send notification
            mail to: 'devops@example.com',
                 subject: "Pipeline Failed: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                 body: "Build failed. Check console output at ${env.BUILD_URL} to view the results."
        }

        unstable {
            echo "Pipeline is unstable!"
        }
    }
}
