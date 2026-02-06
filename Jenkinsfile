pipeline {
    agent any
    
    environment {
        AWS_REGION = 'us-east-1'
        ECR_REGISTRY = '929767729568.dkr.ecr.us-east-1.amazonaws.com'
        ECR_REPO = 'catalog-service'
        ECS_CLUSTER = 'catalog-cluster'
        ECS_SERVICE = 'catalog-service'
        DOCKER_IMAGE = "${ECR_REGISTRY}/${ECR_REPO}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                echo "✅ Code checked out from GitHub"
            }
        }
        
        stage('Build Docker Image') {
            steps {
                dir('catalog-repo') {
                    script {
                        echo "🐳 Building Docker image..."
                        sh "docker build -t ${ECR_REPO}:${BUILD_NUMBER} ."
                        sh "docker tag ${ECR_REPO}:${BUILD_NUMBER} ${DOCKER_IMAGE}:${BUILD_NUMBER}"
                        sh "docker tag ${ECR_REPO}:${BUILD_NUMBER} ${DOCKER_IMAGE}:latest"
                        echo "✅ Docker image built: ${DOCKER_IMAGE}:${BUILD_NUMBER}"
                    }
                }
            }
        }
        
        stage('Login to ECR') {
            steps {
                script {
                    echo "🔐 Logging into AWS ECR..."
                    sh """
                        aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY}
                    """
                    echo "✅ Logged into ECR"
                }
            }
        }
        
        stage('Push to ECR') {
            steps {
                script {
                    echo "📤 Pushing Docker image to ECR..."
                    sh "docker push ${DOCKER_IMAGE}:${BUILD_NUMBER}"
                    sh "docker push ${DOCKER_IMAGE}:latest"
                    echo "✅ Image pushed: ${DOCKER_IMAGE}:${BUILD_NUMBER}"
                }
            }
        }
        
        stage('Deploy to ECS') {
            steps {
                script {
                    echo "🚀 Deploying to ECS..."
                    sh """
                        aws ecs update-service \
                            --cluster ${ECS_CLUSTER} \
                            --service ${ECS_SERVICE} \
                            --force-new-deployment \
                            --region ${AWS_REGION}
                    """
                    echo "✅ Deployment triggered on ECS"
                }
            }
        }
        
        stage('Verify Deployment') {
            steps {
                script {
                    echo "🔍 Waiting for deployment to start..."
                    sleep(time: 30, unit: 'SECONDS')
                    sh """
                        aws ecs describe-services \
                            --cluster ${ECS_CLUSTER} \
                            --services ${ECS_SERVICE} \
                            --region ${AWS_REGION} \
                            --query 'services[0].deployments[0].runningCount'
                    """
                }
            }
        }
    }
    
    post {
        always {
            script {
                echo "🧹 Cleaning up Docker resources..."
                sh 'docker system prune -f || true'
            }
            cleanWs()
        }
        success {
            echo """
            ╔════════════════════════════════════════╗
            ║     ✅ DEPLOYMENT SUCCESSFUL!          ║
            ║                                        ║
            ║     Build Number: #${BUILD_NUMBER}     ║
            ║     Image: ${DOCKER_IMAGE}:${BUILD_NUMBER}
            ╚════════════════════════════════════════╝
            """
        }
        failure {
            echo """
            ╔════════════════════════════════════════╗
            ║     ❌ DEPLOYMENT FAILED!              ║
            ║                                        ║
            ║     Check console output for details   ║
            ╚════════════════════════════════════════╝
            """
        }
    }
}
