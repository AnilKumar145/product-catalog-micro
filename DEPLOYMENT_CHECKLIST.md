# Deployment Checklist - Catalog Service

## ✅ Pre-Deployment Checklist

### Local Setup
- [ ] Python 3.11+ installed
- [ ] Docker Desktop installed and running
- [ ] Git installed
- [ ] AWS CLI v2 installed and configured
- [ ] GitLab account created
- [ ] Jenkins access available

### AWS Account Setup
- [ ] AWS account with admin access
- [ ] AWS CLI configured (`aws configure`)
- [ ] AWS Account ID noted: _______________

---

## 📋 Deployment Steps & Time Estimates

### Step 1: Push to GitLab (30 mins)
- [ ] Create GitLab repository
- [ ] Initialize git in project folder
- [ ] Add remote: `git remote add origin <GITLAB_URL>`
- [ ] Push code: `git push -u origin main`
- [ ] Verify files visible on GitLab

**Commands:**
```bash
cd "c:\Users\618167584\OneDrive - BT Plc\Desktop\Product-catalog\catalog-repo"
git init
git add .
git commit -m "Initial commit"
git remote add origin https://gitlab.com/YOUR_USERNAME/catalog-service.git
git push -u origin main
```

---

### Step 2: Setup Jenkins (1-2 hours)
- [ ] Install Jenkins plugins (Docker, AWS Steps, GitLab)
- [ ] Add GitLab credentials to Jenkins
- [ ] Add AWS credentials to Jenkins
- [ ] Create new Pipeline job
- [ ] Configure job to use Jenkinsfile from GitLab
- [ ] Add environment variables (AWS_ACCOUNT_ID, AWS_REGION)
- [ ] Test build (will fail at AWS steps initially - OK)

---

### Step 3: Setup AWS Infrastructure (2-3 hours)

#### IAM Roles
- [ ] Create ecsTaskExecutionRole
- [ ] Create ecsTaskRole
- [ ] Attach policies to roles

**Commands:**
```bash
aws iam create-role --role-name ecsTaskExecutionRole --assume-role-policy-document file://trust-policy.json
aws iam attach-role-policy --role-name ecsTaskExecutionRole --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy
```

#### Database Setup
- [ ] Create RDS PostgreSQL instance
- [ ] Wait for instance to be available (5-10 mins)
- [ ] Note endpoint: _______________
- [ ] Test connection

**Command:**
```bash
aws rds create-db-instance --db-instance-identifier catalog-db --db-instance-class db.t3.micro --engine postgres --master-username admin --master-user-password <PASSWORD> --allocated-storage 20
```

#### Redis Setup
- [ ] Create ElastiCache Redis cluster
- [ ] Note endpoint: _______________

**Command:**
```bash
aws elasticache create-cache-cluster --cache-cluster-id catalog-redis --cache-node-type cache.t3.micro --engine redis --num-cache-nodes 1
```

#### RabbitMQ Setup
- [ ] Create Amazon MQ broker
- [ ] Note endpoint: _______________

**Command:**
```bash
aws mq create-broker --broker-name catalog-rabbitmq --engine-type RABBITMQ --engine-version 3.11 --host-instance-type mq.t3.micro --publicly-accessible --users Username=admin,Password=<PASSWORD>
```

#### Run Deployment Script
- [ ] Make script executable: `chmod +x deploy-aws.sh`
- [ ] Run: `./deploy-aws.sh`
- [ ] Note VPC ID: _______________
- [ ] Note Subnet IDs: _______________
- [ ] Note Security Group ID: _______________
- [ ] Note ALB DNS: _______________

#### Update Secrets
- [ ] Update database URL in Secrets Manager
- [ ] Update Redis URL in Secrets Manager
- [ ] Update RabbitMQ URL in Secrets Manager
- [ ] Update JWT secret in Secrets Manager

**Commands:**
```bash
aws secretsmanager update-secret --secret-id catalog/database-url --secret-string "postgresql://admin:<PASSWORD>@<RDS_ENDPOINT>:5432/catalog_db"
aws secretsmanager update-secret --secret-id catalog/redis-url --secret-string "redis://<REDIS_ENDPOINT>:6379"
aws secretsmanager update-secret --secret-id catalog/rabbitmq-url --secret-string "amqp://admin:<PASSWORD>@<MQ_ENDPOINT>:5671"
```

---

### Step 4: Build & Push Docker Image (30 mins)
- [ ] Build Docker image locally
- [ ] Test image locally
- [ ] Login to AWS ECR
- [ ] Tag image
- [ ] Push to ECR

**Commands:**
```bash
# Build
docker build -t catalog-service:latest .

# Test locally
docker run -p 8000:8000 --env-file .env catalog-service:latest

# Push to ECR
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
docker tag catalog-service:latest $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/catalog-service:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/catalog-service:latest
```

---

### Step 5: Deploy to ECS (30 mins)
- [ ] Verify task definition registered
- [ ] Verify ECS service created
- [ ] Wait for tasks to be running (2-3 mins)
- [ ] Check task health status
- [ ] Verify load balancer health checks passing

**Commands:**
```bash
# Check service status
aws ecs describe-services --cluster bt-microservices-cluster --services catalog-service

# Check tasks
aws ecs list-tasks --cluster bt-microservices-cluster --service-name catalog-service

# View logs
aws logs tail /ecs/catalog-service --follow
```

---

### Step 6: Get Final URL (5 mins)
- [ ] Get ALB DNS name
- [ ] Test health endpoint
- [ ] Test API docs
- [ ] Test API endpoints

**Commands:**
```bash
# Get URL
ALB_DNS=$(aws elbv2 describe-load-balancers --names catalog-service-alb --query 'LoadBalancers[0].DNSName' --output text)
echo "Service URL: http://$ALB_DNS"

# Test
curl http://$ALB_DNS/health
curl http://$ALB_DNS/api/v1/products
```

**Final URLs:**
- Base URL: http://_______________
- Health: http://_______________/health
- API Docs: http://_______________/docs
- Products API: http://_______________/api/v1/products

---

## 🎯 Total Time Estimate

| Step | Task | Time |
|------|------|------|
| 1 | Push to GitLab | 30 mins |
| 2 | Setup Jenkins | 1-2 hours |
| 3 | Setup AWS Infrastructure | 2-3 hours |
| 4 | Build & Push Docker | 30 mins |
| 5 | Deploy to ECS | 30 mins |
| 6 | Get Final URL | 5 mins |
| **TOTAL** | **End-to-End Deployment** | **5-7 hours** |

**Note:** First-time setup takes longer. Subsequent deployments via Jenkins take ~5-10 minutes.

---

## 🔍 Verification Steps

### After Each Step
- [ ] Step 1: Code visible on GitLab
- [ ] Step 2: Jenkins job created and runs
- [ ] Step 3: AWS resources created (check AWS Console)
- [ ] Step 4: Image visible in ECR
- [ ] Step 5: ECS tasks running (2/2 healthy)
- [ ] Step 6: All URLs responding

### Final Verification
```bash
# Health check
curl http://<ALB_DNS>/health
# Expected: {"status":"healthy","database":"healthy","cache":"healthy","messaging":"healthy"}

# API docs
curl http://<ALB_DNS>/docs
# Expected: HTML page with Swagger UI

# Products endpoint
curl http://<ALB_DNS>/api/v1/products
# Expected: JSON array of products
```

---

## 🚨 Troubleshooting

### Common Issues

**Issue: ECS tasks not starting**
- Check CloudWatch logs: `aws logs tail /ecs/catalog-service --follow`
- Verify secrets exist in Secrets Manager
- Check security group allows port 8000

**Issue: Health checks failing**
- Verify database connection string is correct
- Check Redis/RabbitMQ endpoints
- Ensure security groups allow traffic between services

**Issue: Jenkins build fails**
- Verify AWS credentials in Jenkins
- Check AWS_ACCOUNT_ID environment variable
- Ensure Docker is running on Jenkins agent

**Issue: Cannot access ALB URL**
- Wait 2-3 minutes for DNS propagation
- Check security group allows inbound HTTP (port 80)
- Verify target group has healthy targets

---

## 📊 Cost Tracking

Monthly AWS costs: ~$130
- ECS Fargate: $30
- RDS PostgreSQL: $15
- ElastiCache Redis: $15
- Amazon MQ: $35
- ALB: $20
- Other: $15

---

## 🔄 CI/CD Flow (After Setup)

1. Make code changes locally
2. Commit and push to GitLab: `git push origin main`
3. Jenkins automatically:
   - Runs tests
   - Builds Docker image
   - Pushes to ECR
   - Updates ECS service
4. ECS performs rolling deployment (zero downtime)
5. Service live at ALB URL in ~5 minutes

---

## 📝 Notes

- Keep AWS credentials secure
- Never commit .env file
- Monitor CloudWatch for errors
- Set up billing alerts in AWS
- Enable MFA on AWS account
- Regular security updates

---

## ✅ Deployment Complete!

Once all checkboxes are ticked, your microservice is:
- ✅ Running on AWS ECS
- ✅ Accessible via Load Balancer
- ✅ Auto-deploying via Jenkins
- ✅ Monitored via CloudWatch
- ✅ Scalable and highly available

**Service URL:** http://<YOUR_ALB_DNS>
