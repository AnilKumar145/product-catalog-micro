# 🤖 Complete Beginner's Guide: Jenkins CI/CD Setup

## 👋 What is CI/CD?

**CI/CD** = Continuous Integration / Continuous Deployment

**In simple terms:** When you push code to GitHub, Jenkins automatically:
1. Pulls your code
2. Builds Docker image
3. Pushes to AWS ECR
4. Deploys to ECS

**Result:** Your changes go live automatically! No manual deployment needed.

---

## 🔄 How It Works

```
┌─────────────┐     Webhook      ┌─────────────┐     Deploy      ┌─────────────┐
│   GitHub    │ ───────────────► │   Jenkins   │ ──────────────► │   AWS ECS   │
│  (Your Repo)│                  │ (EC2 Server)│                 │  (Your App) │
└─────────────┘                  └─────────────┘                 └─────────────┘
       │                               │                               │
       │                               ▼                               │
       │                        ┌─────────────┐                        │
       │                        │   AWS ECR   │ ◄──────────────────────┘
       │                        │   (Images)  │      Pull Image
       └────────────────────────►─────────────┘
```

---

## 🛠️ Prerequisites

Before starting, make sure you have:

| Requirement | Status |
|-------------|--------|
| AWS Account with ECS deployed | ✅ (From previous guide) |
| GitHub repository | ✅ |
| AWS CLI configured locally | ✅ |

---

# PHASE 1: LAUNCH JENKINS EC2 INSTANCE

---

## 📦 PART 1: Create EC2 Instance for Jenkins (15 minutes)

### Step 1.1: Create Key Pair (For SSH Access)

```powershell
# Create a key pair to connect to EC2
aws ec2 create-key-pair --key-name jenkins-key --query "KeyMaterial" --output text > jenkins-key.pem

# For Windows, also save the key content
echo "Key saved to jenkins-key.pem"
```

⚠️ **Keep this file safe! You need it to connect to Jenkins server.**

### Step 1.2: Create Security Group for Jenkins

```powershell
# Get your VPC ID
$VPC_ID = aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" --query "Vpcs[0].VpcId" --output text

# Create security group
aws ec2 create-security-group --group-name jenkins-sg --description "Jenkins Server Security Group" --vpc-id $VPC_ID

# Get the security group ID
$JENKINS_SG = aws ec2 describe-security-groups --filters "Name=group-name,Values=jenkins-sg" --query "SecurityGroups[0].GroupId" --output text
echo "Jenkins Security Group: $JENKINS_SG"

# Allow SSH (port 22) - For connecting to server
aws ec2 authorize-security-group-ingress --group-id $JENKINS_SG --protocol tcp --port 22 --cidr 0.0.0.0/0

# Allow Jenkins Web UI (port 8080)
aws ec2 authorize-security-group-ingress --group-id $JENKINS_SG --protocol tcp --port 8080 --cidr 0.0.0.0/0
```

### Step 1.3: Launch EC2 Instance

```powershell
# Launch t2.micro instance (Free Tier eligible!)
aws ec2 run-instances `
    --image-id ami-0c02fb55956c7d316 `
    --count 1 `
    --instance-type t2.micro `
    --key-name jenkins-key `
    --security-group-ids $JENKINS_SG `
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=Jenkins-Server}]" `
    --region us-east-1
```

### Step 1.4: Get Jenkins Server Public IP

Wait 1 minute for the instance to start, then:

```powershell
# Get the public IP
$JENKINS_IP = aws ec2 describe-instances `
    --filters "Name=tag:Name,Values=Jenkins-Server" "Name=instance-state-name,Values=running" `
    --query "Reservations[0].Instances[0].PublicIpAddress" `
    --output text

echo "=============================================="
echo "Jenkins Server IP: $JENKINS_IP"
echo "SSH: ssh -i jenkins-key.pem ec2-user@$JENKINS_IP"
echo "Web UI (after setup): http://${JENKINS_IP}:8080"
echo "=============================================="
```

📝 **Save this IP address! You'll need it multiple times.**

---

# PHASE 2: INSTALL JENKINS ON EC2

---

## 💻 PART 2: Connect to EC2 and Install Jenkins (20 minutes)

### Step 2.1: Connect via SSH

**Option A: Using Git Bash (Recommended for Windows)**

1. Open Git Bash
2. Navigate to where you saved jenkins-key.pem
3. Run:
```bash
chmod 400 jenkins-key.pem
ssh -i jenkins-key.pem ec2-user@YOUR_JENKINS_IP
```

**Option B: Using PuTTY (Windows)**

1. Convert .pem to .ppk using PuTTYgen
2. Connect using PuTTY with the .ppk file

**Option C: Using AWS Console (Easiest)**

1. Go to AWS Console → EC2 → Instances
2. Select Jenkins-Server
3. Click "Connect" → "EC2 Instance Connect" → "Connect"

### Step 2.2: Install Java (Required for Jenkins)

Once connected to EC2, run:

```bash
# Update system
sudo yum update -y

# Install Java 17
sudo yum install java-17-amazon-corretto -y

# Verify Java
java -version
```

### Step 2.3: Install Jenkins

```bash
# Add Jenkins repo
sudo wget -O /etc/yum.repos.d/jenkins.repo https://pkg.jenkins.io/redhat-stable/jenkins.repo

# Import Jenkins key
sudo rpm --import https://pkg.jenkins.io/redhat-stable/jenkins.io-2023.key

# Install Jenkins
sudo yum install jenkins -y

# Start Jenkins
sudo systemctl start jenkins

# Enable Jenkins to start on boot
sudo systemctl enable jenkins

# Check Jenkins status
sudo systemctl status jenkins
```

✅ You should see "active (running)"

### Step 2.4: Install Docker

```bash
# Install Docker
sudo yum install docker -y

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add Jenkins user to Docker group
sudo usermod -aG docker jenkins

# Also add ec2-user to Docker group
sudo usermod -aG docker ec2-user

# Restart Jenkins to apply Docker permissions
sudo systemctl restart jenkins
```

### Step 2.5: Install AWS CLI v2

```bash
# Download AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"

# Unzip and install
unzip awscliv2.zip
sudo ./aws/install

# Verify
aws --version
```

### Step 2.6: Install Git

```bash
sudo yum install git -y
git --version
```

### Step 2.7: Get Jenkins Initial Admin Password

```bash
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```

📝 **Copy this password! You'll need it to unlock Jenkins.**

---

# PHASE 3: CONFIGURE JENKINS WEB UI

---

## 🌐 PART 3: Setup Jenkins via Browser (15 minutes)

### Step 3.1: Open Jenkins Web UI

1. Open browser and go to: `http://YOUR_JENKINS_IP:8080`
2. You should see "Unlock Jenkins" page

### Step 3.2: Unlock Jenkins

1. Paste the initial admin password you copied earlier
2. Click "Continue"

### Step 3.3: Install Plugins

1. Click **"Install suggested plugins"**
2. Wait for plugins to install (takes 3-5 minutes)

### Step 3.4: Create Admin User

Fill in the form:
- Username: `admin`
- Password: `YourSecurePassword123!`
- Full name: `Admin`
- Email: `your@email.com`

Click "Save and Continue"

### Step 3.5: Configure Jenkins URL

1. Keep the default URL: `http://YOUR_JENKINS_IP:8080/`
2. Click "Save and Finish"
3. Click "Start using Jenkins"

🎉 **Jenkins is now running!**

---

## 🔌 PART 4: Install Additional Plugins (5 minutes)

### Step 4.1: Go to Plugin Manager

1. Click **"Manage Jenkins"** (left sidebar)
2. Click **"Plugins"**
3. Click **"Available plugins"** tab

### Step 4.2: Install Required Plugins

Search and install these plugins (check the box next to each):

- ✅ **Docker Pipeline** - For Docker builds
- ✅ **Amazon ECR** - For pushing to ECR
- ✅ **Pipeline: AWS Steps** - For AWS commands
- ✅ **GitHub Integration** - For GitHub webhooks

Click **"Install"** at the bottom

### Step 4.3: Restart Jenkins

After plugins install:
1. Check "Restart Jenkins when installation is complete"
2. Wait for Jenkins to restart
3. Log back in with your admin credentials

---

## 🔐 PART 5: Configure AWS Credentials in Jenkins (10 minutes)

### Step 5.1: Configure AWS CLI on Jenkins Server

Go back to your EC2 SSH session and run:

```bash
# Create AWS credentials directory for Jenkins
sudo mkdir -p /var/lib/jenkins/.aws

# Create credentials file
sudo tee /var/lib/jenkins/.aws/credentials > /dev/null << 'EOF'
[default]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
EOF

# Create config file
sudo tee /var/lib/jenkins/.aws/config > /dev/null << 'EOF'
[default]
region = us-east-1
output = json
EOF

# Set proper ownership
sudo chown -R jenkins:jenkins /var/lib/jenkins/.aws

# Verify AWS CLI works for Jenkins
sudo -u jenkins aws sts get-caller-identity
```

⚠️ **Replace YOUR_ACCESS_KEY and YOUR_SECRET_KEY with your actual keys!**

### Step 5.2: Add Credentials in Jenkins UI

1. Go to Jenkins Dashboard
2. Click **"Manage Jenkins"**
3. Click **"Credentials"**
4. Click **(global)** under Stores
5. Click **"Add Credentials"**

Add these credentials:

**Credential 1: AWS Credentials**
- Kind: `AWS Credentials`
- ID: `aws-credentials`
- Access Key ID: Your AWS Access Key
- Secret Access Key: Your AWS Secret Key

**Credential 2: GitHub Credentials (if private repo)**
- Kind: `Username with password`
- ID: `github-credentials`
- Username: Your GitHub username
- Password: Your GitHub Personal Access Token

---

# PHASE 4: SETUP GITHUB WEBHOOK

---

## 🔗 PART 6: Configure GitHub to Trigger Jenkins (10 minutes)

### Step 6.1: Generate GitHub Personal Access Token

1. Go to GitHub: https://github.com/settings/tokens
2. Click **"Generate new token (classic)"**
3. Name: `Jenkins-CI`
4. Select scopes:
   - ✅ `repo` (Full control of private repos)
   - ✅ `admin:repo_hook` (For webhooks)
5. Click **"Generate token"**
6. 📝 **Copy the token immediately! You won't see it again.**

### Step 6.2: Add Webhook to Your Repository

1. Go to your GitHub repository
2. Click **"Settings"** tab
3. Click **"Webhooks"** in left sidebar
4. Click **"Add webhook"**

Fill in:
- **Payload URL:** `http://YOUR_JENKINS_IP:8080/github-webhook/`
- **Content type:** `application/json`
- **Which events:** `Just the push event`
- Click **"Add webhook"**

### Step 6.3: Verify Webhook

After adding, GitHub will send a test ping. You should see:
- ✅ Green checkmark next to the webhook
- If ❌ red X, check the URL is correct and Jenkins is running

---

# PHASE 5: CREATE JENKINS PIPELINE

---

## 📝 PART 7: Update Jenkinsfile (10 minutes)

### Step 7.1: Update Your Repository's Jenkinsfile

Make sure your `Jenkinsfile` has this content:

```groovy
pipeline {
    agent any
    
    environment {
        AWS_REGION = 'us-east-1'
        ECR_REGISTRY = 'YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com'
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
                    echo "🔍 Waiting for deployment..."
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
                echo "🧹 Cleaning up..."
                sh 'docker system prune -f || true'
            }
            cleanWs()
        }
        success {
            echo """
            ╔════════════════════════════════════════╗
            ║     ✅ DEPLOYMENT SUCCESSFUL!          ║
            ║                                        ║
            ║     Build: #${BUILD_NUMBER}            ║
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
```

⚠️ **Replace `YOUR_ACCOUNT_ID` with your actual 12-digit AWS Account ID!**

### Step 7.2: Commit and Push

```powershell
cd c:\path\to\your\product-catalog-micro
git add .
git commit -m "Update Jenkinsfile for CI/CD"
git push origin main
```

---

## 🔧 PART 8: Create Jenkins Pipeline Job (10 minutes)

### Step 8.1: Create New Pipeline

1. Go to Jenkins Dashboard
2. Click **"New Item"**
3. Enter name: `catalog-service-deploy`
4. Select **"Pipeline"**
5. Click **"OK"**

### Step 8.2: Configure Pipeline

**General Section:**
- ✅ Check **"GitHub project"**
- Project url: `https://github.com/YOUR_USERNAME/YOUR_REPO/`

**Build Triggers Section:**
- ✅ Check **"GitHub hook trigger for GITScm polling"**

**Pipeline Section:**
- Definition: **"Pipeline script from SCM"**
- SCM: **Git**
- Repository URL: `https://github.com/YOUR_USERNAME/YOUR_REPO.git`
- Credentials: Select your GitHub credentials (if private repo)
- Branch: `*/main`
- Script Path: `catalog-repo/Jenkinsfile`

Click **"Save"**

---

# PHASE 6: TEST THE PIPELINE

---

## 🧪 PART 9: Test CI/CD Pipeline (10 minutes)

### Step 9.1: Manual Test Build

1. Go to your pipeline job in Jenkins
2. Click **"Build Now"**
3. Watch the build progress in "Build History"
4. Click on the build number → "Console Output" to see logs

### Step 9.2: Test Automatic Trigger

1. Make a small change in your code (e.g., update README)
2. Commit and push:
```powershell
git add .
git commit -m "Test CI/CD trigger"
git push origin main
```
3. Watch Jenkins - a new build should start automatically!

### Step 9.3: Verify Deployment

After build completes:
```powershell
# Check ECS service
aws ecs describe-services --cluster catalog-cluster --services catalog-service --query "services[0].runningCount"

# Get the new public IP (may change after deployment)
$TASK_ARN = aws ecs list-tasks --cluster catalog-cluster --service-name catalog-service --query "taskArns[0]" --output text
$ENI_ID = aws ecs describe-tasks --cluster catalog-cluster --tasks $TASK_ARN --query "tasks[0].attachments[0].details[?name=='networkInterfaceId'].value" --output text
$PUBLIC_IP = aws ec2 describe-network-interfaces --network-interface-ids $ENI_ID --query "NetworkInterfaces[0].Association.PublicIp" --output text
echo "API URL: http://${PUBLIC_IP}:8000"
```

---

# 🆘 TROUBLESHOOTING

## ❌ Jenkins Not Starting

```bash
# Check status
sudo systemctl status jenkins

# Check logs
sudo journalctl -u jenkins -f

# Restart Jenkins
sudo systemctl restart jenkins
```

## ❌ Docker Permission Denied

```bash
# Add Jenkins to Docker group
sudo usermod -aG docker jenkins

# Restart Jenkins
sudo systemctl restart jenkins

# Verify
sudo -u jenkins docker ps
```

## ❌ AWS CLI Not Working in Jenkins

```bash
# Verify AWS credentials for Jenkins user
sudo -u jenkins aws sts get-caller-identity

# If not working, reconfigure
sudo -u jenkins aws configure
```

## ❌ GitHub Webhook Not Triggering

Check these:
1. Webhook URL ends with `/github-webhook/` (with trailing slash)
2. Jenkins is accessible from internet
3. Security group allows port 8080
4. Check webhook delivery in GitHub Settings → Webhooks

## ❌ Pipeline Failing at ECR Login

```bash
# Test ECR login manually on Jenkins server
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
```

## ❌ Build Takes Too Long

- t2.micro has limited resources
- First Docker build is slow (downloading base images)
- Consider using t2.small if free tier allows

---

# 💰 COST FOR JENKINS

## Free Tier Eligible

| Resource | Cost |
|----------|------|
| EC2 t2.micro (750 hrs/month) | $0 (Free Tier) |
| EBS Storage (30 GB) | $0 (Free Tier) |

## After Free Tier

| Resource | Cost |
|----------|------|
| EC2 t2.micro | ~$8/month |
| EC2 t2.small | ~$16/month |

## Stop Jenkins to Save Money

```powershell
# Get instance ID
$INSTANCE_ID = aws ec2 describe-instances --filters "Name=tag:Name,Values=Jenkins-Server" --query "Reservations[0].Instances[0].InstanceId" --output text

# Stop instance
aws ec2 stop-instances --instance-ids $INSTANCE_ID

# Start instance (when needed)
aws ec2 start-instances --instance-ids $INSTANCE_ID
```

---

# 🔧 USEFUL JENKINS COMMANDS

## Restart Jenkins
```bash
sudo systemctl restart jenkins
```

## View Jenkins Logs
```bash
sudo tail -f /var/log/jenkins/jenkins.log
```

## Check Jenkins Status
```bash
sudo systemctl status jenkins
```

## Update Jenkins
```bash
sudo yum update jenkins -y
sudo systemctl restart jenkins
```

## Backup Jenkins Config
```bash
sudo tar -czvf jenkins-backup.tar.gz /var/lib/jenkins/
```

---

# ✅ CI/CD SETUP CHECKLIST

## Phase 1: EC2 Setup
- [ ] Key pair created (jenkins-key.pem)
- [ ] Security group created with ports 22, 8080
- [ ] EC2 instance launched (t2.micro)
- [ ] Public IP noted

## Phase 2: Jenkins Installation
- [ ] Connected to EC2 via SSH
- [ ] Java installed
- [ ] Jenkins installed and running
- [ ] Docker installed
- [ ] AWS CLI v2 installed
- [ ] Git installed
- [ ] Initial admin password obtained

## Phase 3: Jenkins Configuration
- [ ] Jenkins unlocked in browser
- [ ] Suggested plugins installed
- [ ] Admin user created
- [ ] Additional plugins installed (Docker, ECR, AWS)
- [ ] AWS credentials configured

## Phase 4: GitHub Integration
- [ ] GitHub Personal Access Token created
- [ ] Webhook added to repository
- [ ] Webhook shows green checkmark

## Phase 5: Pipeline Setup
- [ ] Jenkinsfile updated with correct Account ID
- [ ] Changes pushed to GitHub
- [ ] Pipeline job created in Jenkins

## Phase 6: Testing
- [ ] Manual build successful
- [ ] Automatic trigger works (push → build)
- [ ] ECS deployment verified

---

# 🎯 COMPLETE FLOW

After setup, this is what happens automatically:

```
1. You: git push origin main
         ↓
2. GitHub: Sends webhook to Jenkins
         ↓
3. Jenkins: Pulls latest code
         ↓
4. Jenkins: Builds Docker image
         ↓
5. Jenkins: Pushes image to ECR
         ↓
6. Jenkins: Triggers ECS deployment
         ↓
7. ECS: Pulls new image, starts new container
         ↓
8. 🎉 Your changes are live!
```

**Time from push to live: ~3-5 minutes**

---

# 📋 QUICK REFERENCE

```
╔════════════════════════════════════════════════════════════╗
║              JENKINS CI/CD QUICK REFERENCE                 ║
╠════════════════════════════════════════════════════════════╣
║ Jenkins URL:      http://JENKINS_IP:8080                   ║
║ SSH Command:      ssh -i jenkins-key.pem ec2-user@IP       ║
║ Webhook URL:      http://JENKINS_IP:8080/github-webhook/   ║
║ Restart:          sudo systemctl restart jenkins           ║
║ Logs:             sudo tail -f /var/log/jenkins/jenkins.log║
║ Stop EC2:         aws ec2 stop-instances --instance-ids ID ║
║ Start EC2:        aws ec2 start-instances --instance-ids ID║
╚════════════════════════════════════════════════════════════╝
```

---

**🎉 Congratulations! You now have a fully automated CI/CD pipeline!**

Every time you push code to GitHub, it automatically deploys to AWS.

---

*Created: February 2026*  
*Tested with: Jenkins 2.x, AWS CLI v2.x, Docker 20.x, Amazon Linux 2*
