# Quick Start - Deploy Catalog Service

## 🚀 Fastest Path to Deployment

### Option 1: Local Testing (5 minutes)
```bash
# Start all services with Docker Compose
docker-compose up -d

# Access service
# API: http://localhost:8000/docs
# RabbitMQ UI: http://localhost:15672 (guest/guest)
```

### Option 2: Full AWS Deployment (5-7 hours first time)

Follow this order:

1. **DEPLOYMENT_CHECKLIST.md** - Step-by-step checklist with time estimates
2. **DEPLOYMENT_GUIDE.md** - Detailed guide with all commands
3. **deploy-aws.sh** - Automated AWS infrastructure setup script

---

## 📁 Deployment Files Created

| File | Purpose |
|------|---------|
| `Dockerfile` | Container image definition |
| `.dockerignore` | Exclude files from Docker build |
| `docker-compose.yml` | Local development environment |
| `Jenkinsfile` | CI/CD pipeline automation |
| `ecs-task-definition.json` | AWS ECS task configuration |
| `deploy-aws.sh` | AWS infrastructure setup script |
| `DEPLOYMENT_GUIDE.md` | Complete deployment documentation |
| `DEPLOYMENT_CHECKLIST.md` | Step-by-step checklist |

---

## ⏱️ Time Breakdown

| Phase | Duration | Can Skip? |
|-------|----------|-----------|
| **1. GitLab Push** | 30 mins | No |
| **2. Jenkins Setup** | 1-2 hours | Yes (manual deploy) |
| **3. AWS Infrastructure** | 2-3 hours | No |
| **4. Docker Build/Push** | 30 mins | No |
| **5. ECS Deployment** | 30 mins | No |
| **6. Get URL** | 5 mins | No |
| **TOTAL** | **5-7 hours** | - |

**Subsequent deployments via Jenkins: 5-10 minutes**

---

## 🎯 What You'll Get

After deployment:
- ✅ Microservice running on AWS ECS Fargate
- ✅ Auto-scaling (2+ instances)
- ✅ Load balanced with health checks
- ✅ Zero-downtime deployments
- ✅ Automated CI/CD via Jenkins
- ✅ Monitoring via CloudWatch
- ✅ Secure secrets management

**Final URL:** `http://<your-alb-dns>`

---

## 💰 Monthly Cost: ~$130

- ECS Fargate (2 tasks): $30
- RDS PostgreSQL: $15
- ElastiCache Redis: $15
- Amazon MQ: $35
- Load Balancer: $20
- Other: $15

---

## 🔧 Prerequisites

Install these first:
- Git
- Docker Desktop
- AWS CLI v2
- GitLab account
- AWS account

---

## 📋 Next Steps

1. **Start here:** Open `DEPLOYMENT_CHECKLIST.md`
2. **Need details?** Refer to `DEPLOYMENT_GUIDE.md`
3. **Test locally first:** Run `docker-compose up`
4. **Ready for AWS?** Run `./deploy-aws.sh`

---

## 🆘 Need Help?

**Common Commands:**
```bash
# Test locally
docker-compose up -d
curl http://localhost:8000/health

# Deploy to AWS
./deploy-aws.sh

# Get service URL
aws elbv2 describe-load-balancers --names catalog-service-alb --query 'LoadBalancers[0].DNSName' --output text

# View logs
aws logs tail /ecs/catalog-service --follow

# Redeploy
aws ecs update-service --cluster bt-microservices-cluster --service catalog-service --force-new-deployment
```

**Troubleshooting:**
- Check `DEPLOYMENT_GUIDE.md` → "Monitoring & Troubleshooting" section
- View CloudWatch logs
- Check ECS service events
- Verify security groups

---

## 🎓 Learning Path

**New to this?** Follow in order:
1. Test locally with `docker-compose up`
2. Read `DEPLOYMENT_CHECKLIST.md` (understand the flow)
3. Setup AWS infrastructure (Step 3)
4. Manual Docker push (Step 4)
5. Deploy to ECS (Step 5)
6. Setup Jenkins last (Step 2) - for automation

**Experienced?** 
1. Run `./deploy-aws.sh`
2. Push Docker image to ECR
3. Setup Jenkins pipeline
4. Done!

---

## ✅ Success Criteria

Your deployment is successful when:
- [ ] `curl http://<ALB_DNS>/health` returns `{"status":"healthy"}`
- [ ] `http://<ALB_DNS>/docs` shows Swagger UI
- [ ] `http://<ALB_DNS>/api/v1/products` returns data
- [ ] Jenkins builds and deploys automatically on git push
- [ ] ECS shows 2/2 tasks running and healthy

---

## 🔄 Daily Workflow (After Setup)

```bash
# 1. Make changes
vim app/api/v1/products/product_endpoints.py

# 2. Test locally
docker-compose up -d
curl http://localhost:8000/api/v1/products

# 3. Commit and push
git add .
git commit -m "Add new feature"
git push origin main

# 4. Jenkins auto-deploys (5 mins)
# 5. Service live at http://<ALB_DNS>
```

---

**Ready? Start with `DEPLOYMENT_CHECKLIST.md`** ✨
