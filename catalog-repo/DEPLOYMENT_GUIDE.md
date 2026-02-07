# Complete Deployment Guide - Catalog Service

## Overview
This guide walks through deploying the Catalog microservice from development to production on AWS.

---

## Prerequisites

### Required Tools
- Git
- Docker Desktop
- AWS CLI v2
- Jenkins (or access to Jenkins server)
- GitLab account
- AWS Account with appropriate permissions

### AWS Permissions Required
- ECR (Elastic Container Registry)
- ECS (Elastic Container Service)
- VPC, Subnets, Security Groups
- Application Load Balancer
- CloudWatch Logs
- Secrets Manager
- IAM Roles

---

## Step-by-Step Deployment

### **STEP 1: Push to GitLab** (30 minutes)

#### 1.1 Initialize Git Repository
```bash
cd "c:\Users\618167584\OneDrive - BT Plc\Desktop\Product-catalog\catalog-repo"

# Initialize git if not already done
git init
git add .
git commit -m "Initial commit: Catalog microservice"
```

#### 1.2 Create GitLab Repository
1. Go to https://gitlab.com
2. Click "New Project" → "Create blank project"
3. Name: `catalog-service`
4. Visibility: Private
5. Click "Create project"

#### 1.3 Push to GitLab
```bash
# Add GitLab remote (replace with your GitLab URL)
git remote add origin https://gitlab.com/YOUR_USERNAME/catalog-service.git

# Push code
git branch -M main
git push -u origin main
```

**Verification:** Visit your GitLab repository URL to confirm files are uploaded.

---

### **STEP 2: Setup Jenkins CI/CD** (1-2 hours)

#### 2.1 Install Jenkins Plugins
In Jenkins, go to "Manage Jenkins" → "Manage Plugins" → Install:
- Docker Pipeline
- AWS Steps
- GitLab Plugin
- Pipeline

#### 2.2 Configure Jenkins Credentials
Go to "Manage Jenkins" → "Manage Credentials" → Add:

1. **GitLab Credentials**
   - Kind: Username with password
   - ID: `gitlab-credentials`
   - Username: Your GitLab username
   - Password: GitLab Personal Access Token

2. **AWS Credentials**
   - Kind: AWS Credentials
   - ID: `aws-credentials`
   - Access Key ID: Your AWS Access Key
   - Secret Access Key: Your AWS Secret Key

#### 2.3 Create Jenkins Pipeline Job
1. Click "New Item"
2. Name: `catalog-service-pipeline`
3. Type: Pipeline
4. Configuration:
   - **Build Triggers:** GitLab webhook (optional)
   - **Pipeline:**
     - Definition: Pipeline script from SCM
     - SCM: Git
     - Repository URL: Your GitLab repo URL
     - Credentials: Select `gitlab-credentials`
     - Branch: `*/main`
     - Script Path: `Jenkinsfile`

#### 2.4 Configure Jenkins Environment Variables
In Pipeline configuration, add environment variables:
```
AWS_ACCOUNT_ID = <your-aws-account-id>
AWS_REGION = us-east-1
```

#### 2.5 Test Jenkins Pipeline
Click "Build Now" to test (will fail at AWS steps until AWS is configured)

---

### **STEP 3: Setup AWS Infrastructure** (2-3 hours)

#### 3.1 Configure AWS CLI
```bash
aws configure
# Enter:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region: us-east-1
# - Default output format: json
```

#### 3.2 Create IAM Roles

**ECS Task Execution Role:**
```bash
aws iam create-role \
  --role-name ecsTaskExecutionRole \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "ecs-tasks.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }'

aws iam attach-role-policy \
  --role-name ecsTaskExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy
```

**ECS Task Role:**
```bash
aws iam create-role \
  --role-name ecsTaskRole \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "ecs-tasks.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }'
```

#### 3.3 Setup Database (RDS PostgreSQL)
```bash
# Create RDS PostgreSQL instance
aws rds create-db-instance \
  --db-instance-identifier catalog-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password <YOUR_PASSWORD> \
  --allocated-storage 20 \
  --vpc-security-group-ids <YOUR_SG_ID> \
  --publicly-accessible

# Wait for instance to be available (5-10 minutes)
aws rds wait db-instance-available --db-instance-identifier catalog-db

# Get endpoint
aws rds describe-db-instances \
  --db-instance-identifier catalog-db \
  --query 'DBInstances[0].Endpoint.Address' \
  --output text
```

#### 3.4 Setup Redis (ElastiCache)
```bash
aws elasticache create-cache-cluster \
  --cache-cluster-id catalog-redis \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --num-cache-nodes 1
```

#### 3.5 Setup RabbitMQ (Amazon MQ)
```bash
aws mq create-broker \
  --broker-name catalog-rabbitmq \
  --engine-type RABBITMQ \
  --engine-version 3.11 \
  --host-instance-type mq.t3.micro \
  --publicly-accessible \
  --users Username=admin,Password=<YOUR_PASSWORD>
```

#### 3.6 Run Deployment Script
```bash
# Make script executable (Git Bash on Windows)
chmod +x deploy-aws.sh

# Run deployment
./deploy-aws.sh
```

**Note:** Update the secrets in AWS Secrets Manager with actual database/Redis/RabbitMQ URLs after infrastructure is created.

#### 3.7 Update Secrets
```bash
# Get your actual connection strings from above steps
aws secretsmanager update-secret \
  --secret-id catalog/database-url \
  --secret-string "postgresql://admin:<PASSWORD>@<RDS_ENDPOINT>:5432/catalog_db"

aws secretsmanager update-secret \
  --secret-id catalog/redis-url \
  --secret-string "redis://<REDIS_ENDPOINT>:6379"

aws secretsmanager update-secret \
  --secret-id catalog/rabbitmq-url \
  --secret-string "amqp://admin:<PASSWORD>@<MQ_ENDPOINT>:5671"
```

---

### **STEP 4: Build and Push Docker Image** (30 minutes)

#### 4.1 Build Docker Image Locally
```bash
cd "c:\Users\618167584\OneDrive - BT Plc\Desktop\Product-catalog\catalog-repo"

docker build -t catalog-service:latest .
```

#### 4.2 Test Docker Image Locally
```bash
# Create .env file for local testing
cp .env.example .env
# Edit .env with your local credentials

# Run container
docker run -p 8000:8000 --env-file .env catalog-service:latest

# Test in browser: http://localhost:8000/docs
```

#### 4.3 Push to AWS ECR
```bash
# Get AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Tag image
docker tag catalog-service:latest $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/catalog-service:latest

# Push to ECR
docker push $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/catalog-service:latest
```

---

### **STEP 5: Deploy to ECS** (30 minutes)

#### 5.1 Verify Task Definition
```bash
aws ecs describe-task-definition \
  --task-definition catalog-service-task \
  --region us-east-1
```

#### 5.2 Verify Service is Running
```bash
aws ecs describe-services \
  --cluster bt-microservices-cluster \
  --services catalog-service \
  --region us-east-1
```

#### 5.3 Check Service Health
```bash
# Get ALB DNS name
ALB_DNS=$(aws elbv2 describe-load-balancers \
  --names catalog-service-alb \
  --region us-east-1 \
  --query 'LoadBalancers[0].DNSName' \
  --output text)

echo "Service URL: http://$ALB_DNS"

# Test health endpoint
curl http://$ALB_DNS/health
```

---

### **STEP 6: Get Final URL** (5 minutes)

#### 6.1 Get Load Balancer URL
```bash
aws elbv2 describe-load-balancers \
  --names catalog-service-alb \
  --region us-east-1 \
  --query 'LoadBalancers[0].DNSName' \
  --output text
```

**Your service will be available at:**
- **Base URL:** `http://<ALB_DNS>`
- **Health Check:** `http://<ALB_DNS>/health`
- **API Documentation:** `http://<ALB_DNS>/docs`
- **API Endpoints:** `http://<ALB_DNS>/api/v1/products`

#### 6.2 (Optional) Setup Custom Domain
If you have a domain:
```bash
# Create Route53 hosted zone
aws route53 create-hosted-zone --name yourdomain.com --caller-reference $(date +%s)

# Create A record pointing to ALB
# (Use AWS Console or CLI to create alias record)
```

Then access via: `http://catalog.yourdomain.com`

---

## Complete CI/CD Flow

Once everything is set up:

1. **Developer pushes code to GitLab**
   ```bash
   git add .
   git commit -m "Feature: Add new endpoint"
   git push origin main
   ```

2. **Jenkins automatically triggers** (if webhook configured)
   - Runs tests
   - Builds Docker image
   - Pushes to ECR
   - Updates ECS service

3. **ECS performs rolling deployment**
   - Starts new tasks with new image
   - Waits for health checks
   - Drains old tasks
   - Zero downtime deployment

4. **Service is live** at ALB URL

---

## Monitoring & Troubleshooting

### View Logs
```bash
# CloudWatch Logs
aws logs tail /ecs/catalog-service --follow

# ECS Service Events
aws ecs describe-services \
  --cluster bt-microservices-cluster \
  --services catalog-service \
  --query 'services[0].events[0:5]'
```

### Check Task Status
```bash
aws ecs list-tasks \
  --cluster bt-microservices-cluster \
  --service-name catalog-service

aws ecs describe-tasks \
  --cluster bt-microservices-cluster \
  --tasks <TASK_ARN>
```

### Scale Service
```bash
aws ecs update-service \
  --cluster bt-microservices-cluster \
  --service catalog-service \
  --desired-count 3
```

---

## Cost Estimation (Monthly)

- **ECS Fargate (2 tasks):** ~$30
- **RDS PostgreSQL (t3.micro):** ~$15
- **ElastiCache Redis (t3.micro):** ~$15
- **Amazon MQ (t3.micro):** ~$35
- **Application Load Balancer:** ~$20
- **Data Transfer:** ~$10
- **CloudWatch Logs:** ~$5

**Total: ~$130/month**

---

## Rollback Procedure

If deployment fails:
```bash
# Rollback to previous task definition
aws ecs update-service \
  --cluster bt-microservices-cluster \
  --service catalog-service \
  --task-definition catalog-service-task:PREVIOUS_REVISION \
  --force-new-deployment
```

---

## Security Checklist

- ✅ Secrets stored in AWS Secrets Manager
- ✅ No credentials in code
- ✅ Security groups restrict access
- ✅ HTTPS enabled (add SSL certificate to ALB)
- ✅ IAM roles follow least privilege
- ✅ Container image scanning enabled
- ✅ VPC with private subnets for database

---

## Next Steps

1. **Setup HTTPS:** Add SSL certificate to ALB
2. **Setup CI/CD Webhook:** Auto-trigger Jenkins from GitLab
3. **Add Monitoring:** CloudWatch dashboards, alarms
4. **Setup Auto-scaling:** Based on CPU/memory metrics
5. **Add WAF:** Web Application Firewall for security
6. **Implement Blue/Green Deployment:** For safer releases

---

## Support

For issues:
1. Check CloudWatch Logs: `/ecs/catalog-service`
2. Check ECS Service Events
3. Verify security group rules
4. Confirm secrets are correct
5. Check task health status

---

## Quick Reference Commands

```bash
# Redeploy service
aws ecs update-service --cluster bt-microservices-cluster --service catalog-service --force-new-deployment

# View logs
aws logs tail /ecs/catalog-service --follow

# Scale service
aws ecs update-service --cluster bt-microservices-cluster --service catalog-service --desired-count 3

# Get service URL
aws elbv2 describe-load-balancers --names catalog-service-alb --query 'LoadBalancers[0].DNSName' --output text
```
