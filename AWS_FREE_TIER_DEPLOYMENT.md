# 🆓 AWS Free Tier CI/CD Deployment Guide

## Complete Setup: GitHub → Jenkins → AWS (Auto-Deploy on Push)

This guide sets up **automatic deployment** when you push code to GitHub, using **AWS Free Tier** resources.

---

## 📋 Architecture Overview

```
┌─────────────┐    Webhook    ┌──────────────┐    Deploy    ┌─────────────┐
│   GitHub    │──────────────▶│   Jenkins    │─────────────▶│   AWS ECS   │
│   (Code)    │               │  (EC2 t2.micro)             │  (Service)  │
└─────────────┘               └──────────────┘              └─────────────┘
                                     │
                                     ▼
                              ┌──────────────┐
                              │   AWS ECR    │
                              │ (Container)  │
                              └──────────────┘
```

---

## 💰 Free Tier Resources Used

| Service | Free Tier Limit | Our Usage |
|---------|-----------------|-----------|
| EC2 t2.micro | 750 hrs/month | Jenkins Server |
| ECR | 500 MB/month | Docker Images |
| ECS (EC2 launch) | 750 hrs/month | App Container |
| CloudWatch Logs | 5 GB/month | Logs |
| Data Transfer | 15 GB/month | API Traffic |

**Estimated Monthly Cost: $0 - $5** (staying within free tier limits)

---

## 🔧 Prerequisites

1. ✅ AWS Account (Free Tier)
2. ✅ GitHub Account & Repository (You have: `AnilKumar145/product-catalog-micro`)
3. ✅ AWS CLI installed locally
4. ✅ Docker Desktop installed locally

---

## 📁 Step 1: Configure AWS CLI (5 minutes)

### 1.1 Create IAM User
1. Go to AWS Console → IAM → Users → Add User
2. Username: `jenkins-deployer`
3. Access type: **Programmatic access**
4. Attach policies:
   - `AmazonEC2ContainerRegistryFullAccess`
   - `AmazonECS_FullAccess`
   - `AmazonEC2FullAccess`
   - `CloudWatchLogsFullAccess`
5. Download the Access Key CSV

### 1.2 Configure AWS CLI
```powershell
aws configure
```
Enter:
- AWS Access Key ID: `<from CSV>`
- AWS Secret Access Key: `<from CSV>`
- Default region: `us-east-1`
- Output format: `json`

---

## 🐳 Step 2: Create ECR Repository (5 minutes)

```powershell
# Create ECR repository
aws ecr create-repository --repository-name catalog-service --region us-east-1

# Get your AWS Account ID
aws sts get-caller-identity --query Account --output text
```

**Save your Account ID** - you'll need it later!

---

## 🖥️ Step 3: Launch Jenkins EC2 Instance (30 minutes)

### 3.1 Create Security Group
```powershell
# Create security group
aws ec2 create-security-group --group-name jenkins-sg --description "Jenkins Security Group"

# Allow SSH (port 22)
aws ec2 authorize-security-group-ingress --group-name jenkins-sg --protocol tcp --port 22 --cidr 0.0.0.0/0

# Allow Jenkins UI (port 8080)
aws ec2 authorize-security-group-ingress --group-name jenkins-sg --protocol tcp --port 8080 --cidr 0.0.0.0/0

# Allow HTTP (port 80)
aws ec2 authorize-security-group-ingress --group-name jenkins-sg --protocol tcp --port 80 --cidr 0.0.0.0/0
```

### 3.2 Create Key Pair
```powershell
aws ec2 create-key-pair --key-name jenkins-key --query "KeyMaterial" --output text > jenkins-key.pem
```

### 3.3 Launch EC2 Instance (Free Tier t2.micro)
```powershell
# Get latest Amazon Linux 2 AMI ID
$AMI_ID = aws ec2 describe-images --owners amazon --filters "Name=name,Values=amzn2-ami-hvm-*-x86_64-gp2" "Name=state,Values=available" --query "Images | sort_by(@, &CreationDate) | [-1].ImageId" --output text

# Launch instance
aws ec2 run-instances `
    --image-id $AMI_ID `
    --count 1 `
    --instance-type t2.micro `
    --key-name jenkins-key `
    --security-groups jenkins-sg `
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=Jenkins-Server}]" `
    --block-device-mappings "[{`"DeviceName`":`"/dev/xvda`",`"Ebs`":{`"VolumeSize`":20,`"VolumeType`":`"gp2`"}}]"
```

### 3.4 Get Instance Public IP
```powershell
aws ec2 describe-instances --filters "Name=tag:Name,Values=Jenkins-Server" --query "Reservations[0].Instances[0].PublicIpAddress" --output text
```

**Save this IP** - this is your Jenkins URL!

---

## 🔧 Step 4: Install Jenkins on EC2 (30 minutes)

### 4.1 SSH into EC2
```powershell
# Use Git Bash or WSL for SSH
ssh -i jenkins-key.pem ec2-user@<YOUR_EC2_IP>
```

### 4.2 Install Jenkins, Docker, AWS CLI
Run these commands on the EC2 instance:

```bash
# Update system
sudo yum update -y

# Install Java 11 (required for Jenkins)
sudo amazon-linux-extras install java-openjdk11 -y

# Add Jenkins repo
sudo wget -O /etc/yum.repos.d/jenkins.repo https://pkg.jenkins.io/redhat-stable/jenkins.repo
sudo rpm --import https://pkg.jenkins.io/redhat-stable/jenkins.io-2023.key

# Install Jenkins
sudo yum install jenkins -y

# Start Jenkins
sudo systemctl start jenkins
sudo systemctl enable jenkins

# Install Docker
sudo yum install docker -y
sudo systemctl start docker
sudo systemctl enable docker

# Add jenkins user to docker group
sudo usermod -aG docker jenkins
sudo usermod -aG docker ec2-user

# Install AWS CLI v2
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Install Git
sudo yum install git -y

# Restart Jenkins to apply docker permissions
sudo systemctl restart jenkins

# Get initial admin password
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```

**Copy the initial admin password!**

---

## 🌐 Step 5: Configure Jenkins (20 minutes)

### 5.1 Access Jenkins UI
1. Open browser: `http://<YOUR_EC2_IP>:8080`
2. Paste the initial admin password
3. Install suggested plugins
4. Create admin user
5. Save and finish

### 5.2 Install Required Plugins
Go to **Manage Jenkins** → **Plugins** → **Available plugins**

Install:
- Docker Pipeline
- GitHub Integration
- Pipeline
- Pipeline: AWS Steps

### 5.3 Configure AWS Credentials in Jenkins
1. Go to **Manage Jenkins** → **Credentials** → **System** → **Global credentials**
2. Click **Add Credentials**
3. Kind: **AWS Credentials**
4. ID: `aws-credentials`
5. Access Key ID: `<your AWS access key>`
6. Secret Access Key: `<your AWS secret key>`
7. Click **Create**

### 5.4 Configure Jenkins AWS CLI
SSH into EC2 and configure AWS CLI for Jenkins user:
```bash
sudo su - jenkins
aws configure
# Enter your AWS credentials
```

---

## 🔗 Step 6: Setup GitHub Webhook (10 minutes)

### 6.1 Create GitHub Personal Access Token
1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token
3. Select scopes: `repo`, `admin:repo_hook`
4. Copy the token

### 6.2 Add GitHub Credentials to Jenkins
1. Go to **Manage Jenkins** → **Credentials**
2. Add credentials:
   - Kind: **Username with password**
   - Username: Your GitHub username
   - Password: Your Personal Access Token
   - ID: `github-credentials`

### 6.3 Configure GitHub Webhook
1. Go to your GitHub repo: `https://github.com/AnilKumar145/product-catalog-micro`
2. Go to **Settings** → **Webhooks** → **Add webhook**
3. Payload URL: `http://<YOUR_EC2_IP>:8080/github-webhook/`
4. Content type: `application/json`
5. Which events: **Just the push event**
6. Click **Add webhook**

---

## 📝 Step 7: Create Jenkins Pipeline Job (15 minutes)

### 7.1 Create New Pipeline Job
1. Click **New Item**
2. Name: `catalog-service-deploy`
3. Type: **Pipeline**
4. Click **OK**

### 7.2 Configure Pipeline
In the job configuration:

**Build Triggers:**
- ✅ GitHub hook trigger for GITScm polling

**Pipeline Definition:**
- Definition: **Pipeline script from SCM**
- SCM: **Git**
- Repository URL: `https://github.com/AnilKumar145/product-catalog-micro.git`
- Credentials: Select `github-credentials`
- Branch: `*/main`
- Script Path: `catalog-repo/Jenkinsfile`

Click **Save**

---

## 📄 Step 8: Update Jenkinsfile for Free Tier (10 minutes)

Update your Jenkinsfile to work with your setup:

```groovy
pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = "catalog-service"
        DOCKER_TAG = "${BUILD_NUMBER}"
        AWS_REGION = "us-east-1"
        AWS_ACCOUNT_ID = credentials('aws-account-id') // Add this credential
        ECR_REGISTRY = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Build Docker Image') {
            steps {
                dir('catalog-repo') {
                    sh "docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} ."
                    sh "docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest"
                }
            }
        }
        
        stage('Push to ECR') {
            steps {
                sh '''
                    aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY}
                    docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${ECR_REGISTRY}/${DOCKER_IMAGE}:${DOCKER_TAG}
                    docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${ECR_REGISTRY}/${DOCKER_IMAGE}:latest
                    docker push ${ECR_REGISTRY}/${DOCKER_IMAGE}:${DOCKER_TAG}
                    docker push ${ECR_REGISTRY}/${DOCKER_IMAGE}:latest
                '''
            }
        }
        
        stage('Deploy to ECS') {
            steps {
                sh '''
                    aws ecs update-service \
                        --cluster catalog-cluster \
                        --service catalog-service \
                        --force-new-deployment \
                        --region ${AWS_REGION}
                '''
            }
        }
    }
    
    post {
        always {
            sh 'docker system prune -f || true'
            cleanWs()
        }
        success {
            echo '✅ Deployment successful!'
        }
        failure {
            echo '❌ Deployment failed!'
        }
    }
}
```

---

## 🚀 Step 9: Create ECS Cluster (Free Tier) (30 minutes)

### 9.1 Create ECS Cluster with EC2 Launch Type
```powershell
# Create ECS cluster
aws ecs create-cluster --cluster-name catalog-cluster --region us-east-1
```

### 9.2 Create ECS Task Execution Role
```powershell
# Create trust policy file
@"
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {"Service": "ecs-tasks.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }
    ]
}
"@ | Out-File -FilePath trust-policy.json -Encoding UTF8

# Create role
aws iam create-role --role-name ecsTaskExecutionRole --assume-role-policy-document file://trust-policy.json

# Attach policy
aws iam attach-role-policy --role-name ecsTaskExecutionRole --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy
aws iam attach-role-policy --role-name ecsTaskExecutionRole --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly
```

### 9.3 Create CloudWatch Log Group
```powershell
aws logs create-log-group --log-group-name /ecs/catalog-service --region us-east-1
```

### 9.4 Register Task Definition
Create a simplified task definition for free tier:

```powershell
# Get your account ID
$ACCOUNT_ID = aws sts get-caller-identity --query Account --output text

# Create task definition JSON
@"
{
    "family": "catalog-service-task",
    "networkMode": "awsvpc",
    "requiresCompatibilities": ["FARGATE"],
    "cpu": "256",
    "memory": "512",
    "executionRoleArn": "arn:aws:iam::${ACCOUNT_ID}:role/ecsTaskExecutionRole",
    "containerDefinitions": [
        {
            "name": "catalog-service",
            "image": "${ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com/catalog-service:latest",
            "portMappings": [
                {
                    "containerPort": 8000,
                    "protocol": "tcp"
                }
            ],
            "essential": true,
            "environment": [
                {"name": "APP_NAME", "value": "Catalog Service"},
                {"name": "APP_VERSION", "value": "1.0.0"},
                {"name": "DATABASE_URL", "value": "sqlite:///./catalog.db"},
                {"name": "JWT_SECRET_KEY", "value": "your-secret-key-change-in-production"},
                {"name": "AUTH_SERVICE_URL", "value": "http://localhost:8001"},
                {"name": "REDIS_URL", "value": "redis://localhost:6379"},
                {"name": "RABBITMQ_URL", "value": "amqp://guest:guest@localhost:5672/"}
            ],
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-group": "/ecs/catalog-service",
                    "awslogs-region": "us-east-1",
                    "awslogs-stream-prefix": "ecs"
                }
            }
        }
    ]
}
"@ | Out-File -FilePath task-definition.json -Encoding UTF8

# Register task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json --region us-east-1
```

### 9.5 Create VPC, Subnets, Security Group (for ECS)
```powershell
# Get default VPC
$VPC_ID = aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" --query "Vpcs[0].VpcId" --output text

# Get subnets
$SUBNETS = aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query "Subnets[*].SubnetId" --output text

# Create security group for ECS
aws ec2 create-security-group --group-name ecs-catalog-sg --description "ECS Catalog Service SG" --vpc-id $VPC_ID

# Allow inbound on port 8000
$SG_ID = aws ec2 describe-security-groups --filters "Name=group-name,Values=ecs-catalog-sg" --query "SecurityGroups[0].GroupId" --output text

aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 8000 --cidr 0.0.0.0/0
```

### 9.6 Create ECS Service
```powershell
# Get first two subnets
$SUBNET1 = (aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query "Subnets[0].SubnetId" --output text)
$SUBNET2 = (aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query "Subnets[1].SubnetId" --output text)

# Create ECS service
aws ecs create-service `
    --cluster catalog-cluster `
    --service-name catalog-service `
    --task-definition catalog-service-task `
    --desired-count 1 `
    --launch-type FARGATE `
    --network-configuration "awsvpcConfiguration={subnets=[$SUBNET1,$SUBNET2],securityGroups=[$SG_ID],assignPublicIp=ENABLED}" `
    --region us-east-1
```

---

## 🧪 Step 10: Test the Full Pipeline (10 minutes)

### 10.1 Initial Manual Build
1. Go to Jenkins: `http://<YOUR_EC2_IP>:8080`
2. Click on `catalog-service-deploy`
3. Click **Build Now**
4. Watch the console output

### 10.2 Test Automatic Deployment
1. Make a small change to any file in your repo
2. Commit and push:
```powershell
cd c:\Users\DELL\Downloads\Product-catalog\product-catalog-micro
git add .
git commit -m "Test automatic deployment"
git push origin main
```
3. Watch Jenkins automatically trigger a build!

### 10.3 Get Your Service URL
```powershell
# Get task ARN
$TASK_ARN = aws ecs list-tasks --cluster catalog-cluster --service-name catalog-service --query "taskArns[0]" --output text

# Get task details including public IP
aws ecs describe-tasks --cluster catalog-cluster --tasks $TASK_ARN --query "tasks[0].attachments[0].details[?name=='networkInterfaceId'].value" --output text

# Get public IP from network interface
$ENI_ID = aws ecs describe-tasks --cluster catalog-cluster --tasks $TASK_ARN --query "tasks[0].attachments[0].details[?name=='networkInterfaceId'].value" --output text

aws ec2 describe-network-interfaces --network-interface-ids $ENI_ID --query "NetworkInterfaces[0].Association.PublicIp" --output text
```

**Your API is now live at:** `http://<PUBLIC_IP>:8000`

---

## 📊 Quick Reference

### Your URLs
| Service | URL |
|---------|-----|
| Jenkins | `http://<EC2_IP>:8080` |
| API Health | `http://<ECS_IP>:8000/health` |
| API Docs | `http://<ECS_IP>:8000/docs` |
| Products API | `http://<ECS_IP>:8000/api/v1/products` |

### Useful Commands
```powershell
# Check ECS service status
aws ecs describe-services --cluster catalog-cluster --services catalog-service

# View logs
aws logs tail /ecs/catalog-service --follow

# Force new deployment
aws ecs update-service --cluster catalog-cluster --service catalog-service --force-new-deployment

# Scale service
aws ecs update-service --cluster catalog-cluster --service catalog-service --desired-count 2
```

---

## 🔄 How Auto-Deployment Works

```
1. You push code to GitHub
         ↓
2. GitHub Webhook triggers Jenkins
         ↓
3. Jenkins checks out code
         ↓
4. Jenkins builds Docker image
         ↓
5. Jenkins pushes to AWS ECR
         ↓
6. Jenkins tells ECS to update
         ↓
7. ECS pulls new image & deploys
         ↓
8. New version is live! 🎉
```

---

## 💡 Tips for Staying in Free Tier

1. **Stop Jenkins EC2** when not using:
   ```powershell
   aws ec2 stop-instances --instance-ids <INSTANCE_ID>
   ```

2. **Scale ECS to 0** when not needed:
   ```powershell
   aws ecs update-service --cluster catalog-cluster --service catalog-service --desired-count 0
   ```

3. **Clean up old Docker images** in ECR

4. **Set billing alerts** in AWS Console

---

## 🆘 Troubleshooting

### Jenkins Build Fails
```bash
# SSH to Jenkins EC2
ssh -i jenkins-key.pem ec2-user@<EC2_IP>

# Check Jenkins logs
sudo tail -f /var/log/jenkins/jenkins.log

# Check Docker works
docker ps
```

### ECS Task Not Starting
```powershell
# Check service events
aws ecs describe-services --cluster catalog-cluster --services catalog-service --query "services[0].events[0:5]"

# Check task failures
aws ecs describe-tasks --cluster catalog-cluster --tasks <TASK_ARN>
```

### Webhook Not Triggering
1. Check GitHub webhook delivery history
2. Ensure Jenkins URL is accessible from internet
3. Check security group allows port 8080

---

## ✅ Completion Checklist

- [ ] AWS CLI configured
- [ ] ECR repository created
- [ ] Jenkins EC2 instance running
- [ ] Jenkins plugins installed
- [ ] AWS credentials added to Jenkins
- [ ] GitHub webhook configured
- [ ] ECS cluster created
- [ ] Task definition registered
- [ ] ECS service running
- [ ] Pipeline tested with manual build
- [ ] Automatic deployment tested with git push

---

**Congratulations! 🎉** You now have a complete CI/CD pipeline that automatically deploys your code when you push to GitHub!
