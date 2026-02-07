# 🎓 Complete Beginner's Guide: Deploy to AWS (ECS Fargate)

## 👋 Welcome!

This guide is for **complete beginners**. Follow each step carefully and your app will be live on AWS!

**Author:** Auto-generated deployment guide  
**Last Updated:** February 2026  
**Estimated Time:** 1-2 hours for first deployment

---

## 📚 Glossary - What These Terms Mean

| Term | What It Means (Simple Explanation) |
|------|-----------------------------------|
| **AWS** | Amazon's cloud - like renting a computer on the internet |
| **EC2** | A virtual computer running in AWS |
| **ECR** | A place to store your Docker images (like Google Drive for app packages) |
| **ECS** | A service that runs your Docker containers |
| **Fargate** | AWS runs your containers - you don't manage servers |
| **Docker** | A way to package your app so it runs the same everywhere |
| **Security Group** | A firewall that controls what traffic can reach your app |
| **VPC** | Virtual Private Cloud - your private network in AWS |
| **Subnet** | A section of your VPC network |

---

## 🛠️ Prerequisites Checklist

Before you start, make sure you have:

| Requirement | Status | How to Get It |
|-------------|--------|---------------|
| GitHub Account | ⬜ | https://github.com |
| AWS Account (Free Tier) | ⬜ | https://aws.amazon.com/free |
| AWS CLI installed | ⬜ | Part 2 of this guide |
| Docker Desktop installed | ⬜ | https://docker.com/products/docker-desktop |

---

# PHASE 1: ONE-TIME SETUP

This phase only needs to be done once by your team lead.

---

## 📦 PART 1: Setting Up AWS Account (15 minutes)

### Step 1.1: Create AWS Account

1. Go to: https://aws.amazon.com/free
2. Click **"Create a Free Account"**
3. Enter your email and password
4. Choose **"Personal"** account type
5. Enter your credit card (Required for verification, but Free Tier = $0)
6. Complete phone verification
7. Choose **"Basic Support - Free"**

⚠️ **Important:** AWS Free Tier gives you 12 months of free usage!

### Step 1.2: First Login to AWS

1. Go to: https://console.aws.amazon.com
2. Sign in with your email
3. You'll see the AWS Console (your cloud control panel!)

---

## 💻 PART 2: Install AWS CLI (10 minutes)

### Windows Installation:
1. Download: https://awscli.amazonaws.com/AWSCLIV2.msi
2. Run the installer → Next → Next → Install → Finish
3. **IMPORTANT:** Close and reopen PowerShell after installation!

### Mac Installation:
```bash
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /
```

### Linux Installation:
```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

### Verify Installation:
```powershell
aws --version
```
✅ You should see: `aws-cli/2.x.x ...`

---

## 🔑 PART 3: Create AWS Access Keys (10 minutes)

### Step 3.1: Create IAM User

1. Go to AWS Console: https://console.aws.amazon.com
2. Search for **"IAM"** in the top search bar
3. Click **"IAM"** (Identity and Access Management)
4. In left menu, click **"Users"**
5. Click **"Create user"** button
6. User name: `deployer` (or your preferred name)
7. Click **"Next"**
8. Select **"Attach policies directly"**
9. Search and check these policies:
   - ✅ `AdministratorAccess`
10. Click **"Next"** → **"Create user"**

### Step 3.2: Create Access Key

1. Click on the user you just created
2. Go to **"Security credentials"** tab
3. Scroll down to **"Access keys"** section
4. Click **"Create access key"**
5. Select **"Command Line Interface (CLI)"**
6. Check the confirmation checkbox
7. Click **"Next"** → **"Create access key"**
8. ⚠️ **CRITICAL:** Download the .csv file or copy BOTH keys now!
   - Access Key ID: `AKIA...`
   - Secret Access Key: `xxxxx...`

**🔒 SAVE THESE KEYS SECURELY! You cannot see the secret key again!**

---

## ⚙️ PART 4: Configure AWS CLI (5 minutes)

### Step 4.1: Run AWS Configure

Open PowerShell/Terminal and run:
```powershell
aws configure
```

Enter when prompted:
```
AWS Access Key ID [None]: <paste your access key>
AWS Secret Access Key [None]: <paste your secret key>
Default region name [None]: us-east-1
Default output format [None]: json
```

### Step 4.2: Verify Configuration

```powershell
aws sts get-caller-identity
```

✅ You should see JSON with your Account ID:
```json
{
    "UserId": "AIDA...",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/deployer"
}
```

### Step 4.3: Save Your Account ID

```powershell
aws sts get-caller-identity --query Account --output text
```

📝 **Write down this 12-digit number! You'll need it multiple times.**

---

## 🏗️ PART 5: Create AWS Infrastructure (20 minutes)

Run each command one by one. Replace `YOUR_ACCOUNT_ID` with your 12-digit account ID.

### Step 5.1: Create ECR Repository (Docker Image Storage)

```powershell
aws ecr create-repository --repository-name catalog-service --region us-east-1
```

✅ Expected: JSON with `repositoryUri`

### Step 5.2: Create CloudWatch Log Group (For Logs)

```powershell
aws logs create-log-group --log-group-name /ecs/catalog-service --region us-east-1
```

✅ Expected: No output (that's good!)

### Step 5.3: Create ECS Cluster

```powershell
aws ecs create-cluster --cluster-name catalog-cluster --region us-east-1
```

✅ Expected: JSON with `clusterArn`

### Step 5.4: Create IAM Role for ECS

First, create the trust policy file. Open a text editor and save this as `trust-policy.json`:

```json
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
```

Then run these commands from the folder containing `trust-policy.json`:

```powershell
# Create the IAM role
aws iam create-role --role-name ecsTaskExecutionRole --assume-role-policy-document file://trust-policy.json

# Attach required policies
aws iam attach-role-policy --role-name ecsTaskExecutionRole --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy

aws iam attach-role-policy --role-name ecsTaskExecutionRole --policy-arn arn:aws:iam::aws:policy/CloudWatchLogsFullAccess

aws iam attach-role-policy --role-name ecsTaskExecutionRole --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly
```

### Step 5.5: Get VPC and Subnet Information

```powershell
# Get your default VPC ID
$VPC_ID = aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" --query "Vpcs[0].VpcId" --output text
echo "VPC ID: $VPC_ID"

# Get subnet IDs
$SUBNET1 = aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query "Subnets[0].SubnetId" --output text
$SUBNET2 = aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query "Subnets[1].SubnetId" --output text
echo "Subnet 1: $SUBNET1"
echo "Subnet 2: $SUBNET2"
```

📝 **Save these values:**
- VPC ID: `vpc-xxxxx`
- Subnet 1: `subnet-xxxxx`
- Subnet 2: `subnet-xxxxx`

### Step 5.6: Create Security Group

```powershell
# Create security group
aws ec2 create-security-group --group-name ecs-catalog-sg --description "Catalog Service Security Group" --vpc-id $VPC_ID

# Get the security group ID
$SG_ID = aws ec2 describe-security-groups --filters "Name=group-name,Values=ecs-catalog-sg" --query "SecurityGroups[0].GroupId" --output text
echo "Security Group ID: $SG_ID"

# ⚠️ CRITICAL: Allow traffic on port 8000
aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 8000 --cidr 0.0.0.0/0
```

📝 **Save Security Group ID:** `sg-xxxxx`

---

# PHASE 2: DEPLOY YOUR APPLICATION

This phase is done every time you want to deploy.

---

## 🐳 PART 6: Build and Push Docker Image (15 minutes)

### Step 6.1: Navigate to Your Project

```powershell
cd c:\path\to\your\catalog-repo
```

### Step 6.2: Login to ECR

```powershell
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
```

✅ Expected: `Login Succeeded`

### Step 6.3: Build Docker Image

```powershell
docker build -t catalog-service:latest .
```

⏳ First build takes 2-5 minutes

### Step 6.4: Tag Image for ECR

```powershell
docker tag catalog-service:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/catalog-service:latest
```

### Step 6.5: Push to ECR

```powershell
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/catalog-service:latest
```

⏳ This takes 2-5 minutes depending on image size

---

## 🚀 PART 7: Deploy to ECS (20 minutes)

### Step 7.1: Create Task Definition File

Create a file named `task-def.json` with this content.  
⚠️ **Replace `YOUR_ACCOUNT_ID` (appears 2 times):**

```json
{
    "family": "catalog-service-task",
    "networkMode": "awsvpc",
    "requiresCompatibilities": ["FARGATE"],
    "cpu": "256",
    "memory": "512",
    "executionRoleArn": "arn:aws:iam::YOUR_ACCOUNT_ID:role/ecsTaskExecutionRole",
    "containerDefinitions": [
        {
            "name": "catalog-service",
            "image": "YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/catalog-service:latest",
            "portMappings": [{"containerPort": 8000, "protocol": "tcp"}],
            "essential": true,
            "environment": [
                {"name": "APP_NAME", "value": "Catalog Service"},
                {"name": "APP_VERSION", "value": "1.0.0"},
                {"name": "DATABASE_URL", "value": "postgresql://user:pass@host:5432/db"},
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
```

### Step 7.2: Register Task Definition

```powershell
aws ecs register-task-definition --cli-input-json file://task-def.json --region us-east-1
```

### Step 7.3: Create ECS Service

⚠️ **Use your saved Subnet IDs and Security Group ID:**

```powershell
# Set your variables (use your actual values)
$SUBNET1 = "subnet-xxxxx"
$SUBNET2 = "subnet-xxxxx"
$SG_ID = "sg-xxxxx"

# Create the service
aws ecs create-service --cluster "catalog-cluster" --service-name "catalog-service" --task-definition "catalog-service-task" --desired-count 1 --launch-type "FARGATE" --network-configuration "awsvpcConfiguration={subnets=[$SUBNET1,$SUBNET2],securityGroups=[$SG_ID],assignPublicIp=ENABLED}" --region "us-east-1"
```

#### ⚠️ If You Get "not idempotent" Error:
This means the service already exists. Update it instead:
```powershell
aws ecs update-service --cluster "catalog-cluster" --service "catalog-service" --network-configuration "awsvpcConfiguration={subnets=[$SUBNET1,$SUBNET2],securityGroups=[$SG_ID],assignPublicIp=ENABLED}" --force-new-deployment --region "us-east-1"
```

---

## 🌐 PART 8: Get Your API URL! 🎉

### Step 8.1: Wait for Service to Start

Check status (wait until it shows `1`):
```powershell
aws ecs describe-services --cluster "catalog-cluster" --services "catalog-service" --query "services[0].runningCount" --output text
```

### Step 8.2: Get Public IP

```powershell
# Get the task ARN
$TASK_ARN = aws ecs list-tasks --cluster catalog-cluster --service-name catalog-service --query "taskArns[0]" --output text
echo "Task ARN: $TASK_ARN"

# Get network interface ID
$ENI_ID = aws ecs describe-tasks --cluster catalog-cluster --tasks $TASK_ARN --query "tasks[0].attachments[0].details[?name=='networkInterfaceId'].value" --output text
echo "Network Interface: $ENI_ID"

# Verify security group is attached (CRITICAL!)
aws ec2 describe-network-interfaces --network-interface-ids $ENI_ID --query "NetworkInterfaces[0].Groups"

# Get Public IP
$PUBLIC_IP = aws ec2 describe-network-interfaces --network-interface-ids $ENI_ID --query "NetworkInterfaces[0].Association.PublicIp" --output text

echo "==========================================="
echo "YOUR API IS LIVE!"
echo "   http://${PUBLIC_IP}:8000"
echo "   http://${PUBLIC_IP}:8000/docs"
echo "   http://${PUBLIC_IP}:8000/health"
echo "==========================================="
```

### Step 8.3: Test Your API!

Open in your browser:
- `http://YOUR_PUBLIC_IP:8000` - Service info
- `http://YOUR_PUBLIC_IP:8000/docs` - Swagger API Documentation
- `http://YOUR_PUBLIC_IP:8000/health` - Health check

🎉 **Congratulations! Your API is now live on AWS!**

---

# 🔧 USEFUL COMMANDS REFERENCE

## Check Service Status
```powershell
aws ecs describe-services --cluster "catalog-cluster" --services "catalog-service" --query "services[0].[status,runningCount,desiredCount]"
```

## View Container Logs
```powershell
aws logs tail /ecs/catalog-service --follow
```

## Force New Deployment (After Pushing New Image)
```powershell
aws ecs update-service --cluster "catalog-cluster" --service "catalog-service" --force-new-deployment
```

## Scale Service Up/Down
```powershell
# Stop service (save money)
aws ecs update-service --cluster "catalog-cluster" --service "catalog-service" --desired-count 0

# Start service
aws ecs update-service --cluster "catalog-cluster" --service "catalog-service" --desired-count 1

# Scale to multiple instances
aws ecs update-service --cluster "catalog-cluster" --service "catalog-service" --desired-count 3
```

## Check Why Tasks Are Failing
```powershell
aws ecs describe-services --cluster "catalog-cluster" --services "catalog-service" --query "services[0].events[0:5]"
```

---

# 🆘 TROUBLESHOOTING GUIDE

## ❌ Error: "not idempotent"
**Meaning:** Resource already exists  
**Solution:** Use `update-service` instead of `create-service`

## ❌ Error: "Role not found"
**Solution:** Create the IAM role first (Part 5.4), wait 30 seconds after creation

## ❌ Error: "InvalidGroup.Duplicate"
**Meaning:** Security group already exists  
**Solution:** This is fine! Just get the existing ID:
```powershell
$SG_ID = aws ec2 describe-security-groups --filters "Name=group-name,Values=ecs-catalog-sg" --query "SecurityGroups[0].GroupId" --output text
```

## ❌ Site Can't Be Reached / Connection Timeout

This is usually a **security group** issue. Check these:

### 1. Verify Port 8000 is Open:
```powershell
aws ec2 describe-security-groups --group-ids $SG_ID --query "SecurityGroups[0].IpPermissions"
```
You should see `FromPort: 8000` and `ToPort: 8000`

### 2. Verify Security Group is Attached to Task:
```powershell
$TASK_ARN = aws ecs list-tasks --cluster catalog-cluster --service-name catalog-service --query "taskArns[0]" --output text
$ENI_ID = aws ecs describe-tasks --cluster catalog-cluster --tasks $TASK_ARN --query "tasks[0].attachments[0].details[?name=='networkInterfaceId'].value" --output text
aws ec2 describe-network-interfaces --network-interface-ids $ENI_ID --query "NetworkInterfaces[0].Groups"
```

⚠️ **If it shows "default" security group instead of "ecs-catalog-sg":**
```powershell
# Stop old tasks
$TASKS = aws ecs list-tasks --cluster catalog-cluster --service-name catalog-service --query "taskArns" --output json | ConvertFrom-Json
foreach ($task in $TASKS) {
    aws ecs stop-task --cluster catalog-cluster --task $task
}

# Force new deployment with correct security group
aws ecs update-service --cluster "catalog-cluster" --service "catalog-service" --network-configuration "awsvpcConfiguration={subnets=[$SUBNET1,$SUBNET2],securityGroups=[$SG_ID],assignPublicIp=ENABLED}" --force-new-deployment --region "us-east-1"
```

## ❌ Container Keeps Restarting

Check logs for errors:
```powershell
aws logs tail /ecs/catalog-service --since 10m
```

Common causes:
- Wrong DATABASE_URL
- Missing environment variables
- Application crash on startup

## ❌ "ResourceInitializationError" / "Connection to ECR failed"

This happens when the task can't pull the Docker image. Solutions:
1. Make sure you pushed the image to ECR
2. Verify the image exists:
```powershell
aws ecr describe-images --repository-name catalog-service
```
3. Ensure the task execution role has ECR permissions

---

# 💰 COST MANAGEMENT (Stay in Free Tier!)

## AWS Free Tier Limits (12 months)
| Service | Free Limit per Month |
|---------|---------------------|
| EC2 t2.micro | 750 hours |
| ECS Fargate | 750 hours |
| ECR Storage | 500 MB |
| CloudWatch Logs | 5 GB |

## Money-Saving Tips

### 1. Stop Service When Not Using:
```powershell
aws ecs update-service --cluster "catalog-cluster" --service "catalog-service" --desired-count 0
```

### 2. Set Billing Alerts:
1. Go to AWS Console → Billing → Budgets
2. Create a budget for $5 or $10
3. Get email alerts before you exceed it

### 3. Clean Up Unused Resources:
```powershell
# Delete everything when done learning
aws ecs delete-service --cluster catalog-cluster --service catalog-service --force
aws ecs delete-cluster --cluster catalog-cluster
aws ecr delete-repository --repository-name catalog-service --force
aws logs delete-log-group --log-group-name /ecs/catalog-service
```

---

# ✅ DEPLOYMENT CHECKLIST

Use this checklist for each deployment:

## First-Time Setup (Phase 1)
- [ ] AWS account created
- [ ] AWS CLI installed
- [ ] IAM user created with access keys
- [ ] AWS CLI configured (`aws configure`)
- [ ] ECR repository created
- [ ] CloudWatch log group created
- [ ] ECS cluster created
- [ ] IAM role created and policies attached
- [ ] VPC and subnet IDs noted
- [ ] Security group created with port 8000 open

## Each Deployment (Phase 2)
- [ ] Docker image built
- [ ] Docker image tagged for ECR
- [ ] Docker image pushed to ECR
- [ ] Task definition registered (or updated)
- [ ] ECS service created/updated
- [ ] Verified runningCount = 1
- [ ] Security group verified on network interface
- [ ] Public IP obtained
- [ ] API tested in browser

---

# 📋 QUICK REFERENCE CARD

```
╔═══════════════════════════════════════════════════════════╗
║              AWS DEPLOYMENT QUICK REFERENCE               ║
╠═══════════════════════════════════════════════════════════╣
║ Get Account ID:   aws sts get-caller-identity             ║
║ Login to ECR:     aws ecr get-login-password | docker ... ║
║ Build Image:      docker build -t name:tag .              ║
║ Push Image:       docker push <ecr-url>/name:tag          ║
║ Deploy:           aws ecs update-service --force-...      ║
║ View Logs:        aws logs tail /ecs/catalog-service      ║
║ Check Status:     aws ecs describe-services ...           ║
║ Stop Service:     --desired-count 0                       ║
║ Start Service:    --desired-count 1                       ║
║ Get Task IP:      See Part 8.2 commands                   ║
╚═══════════════════════════════════════════════════════════╝
```

---

# 🎯 NEXT STEPS

After manual deployment works, you can set up:

1. **CI/CD Pipeline with Jenkins** - Auto-deploy when you push to GitHub
2. **Custom Domain** - Use Route53 to get a nice URL like `api.yourapp.com`
3. **HTTPS** - Add SSL certificate for secure connections
4. **Load Balancer** - For production traffic distribution
5. **Auto-Scaling** - Automatically add more containers under high load

---

**🎉 Congratulations on completing your AWS deployment!**

For questions or issues, check the Troubleshooting section above.

---

*Created: February 2026*  
*Tested with: AWS CLI v2.x, Docker 29.x, Windows 11 / PowerShell*
