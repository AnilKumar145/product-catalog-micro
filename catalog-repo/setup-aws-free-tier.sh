#!/bin/bash
# =====================================================
# AWS Free Tier Setup Script for CI/CD Pipeline
# =====================================================
# This script sets up the required AWS infrastructure
# for the catalog-service CI/CD pipeline
# =====================================================

set -e

echo "=============================================="
echo "   AWS Free Tier CI/CD Setup Script"
echo "=============================================="

# Configuration
AWS_REGION="us-east-1"
CLUSTER_NAME="catalog-cluster"
SERVICE_NAME="catalog-service"
ECR_REPO_NAME="catalog-service"
LOG_GROUP="/ecs/catalog-service"

# Get AWS Account ID
echo ""
echo "🔍 Getting AWS Account ID..."
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "   Account ID: $AWS_ACCOUNT_ID"

# Step 1: Create ECR Repository
echo ""
echo "📦 Step 1: Creating ECR Repository..."
aws ecr create-repository \
    --repository-name $ECR_REPO_NAME \
    --region $AWS_REGION 2>/dev/null || echo "   ECR repository already exists"
echo "   ✅ ECR Repository: $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME"

# Step 2: Create CloudWatch Log Group
echo ""
echo "📊 Step 2: Creating CloudWatch Log Group..."
aws logs create-log-group \
    --log-group-name $LOG_GROUP \
    --region $AWS_REGION 2>/dev/null || echo "   Log group already exists"
echo "   ✅ Log Group: $LOG_GROUP"

# Step 3: Create ECS Task Execution Role
echo ""
echo "🔐 Step 3: Creating ECS Task Execution Role..."
cat > /tmp/trust-policy.json << 'EOF'
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
EOF

aws iam create-role \
    --role-name ecsTaskExecutionRole \
    --assume-role-policy-document file:///tmp/trust-policy.json 2>/dev/null || echo "   Role already exists"

aws iam attach-role-policy \
    --role-name ecsTaskExecutionRole \
    --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy 2>/dev/null || true

aws iam attach-role-policy \
    --role-name ecsTaskExecutionRole \
    --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly 2>/dev/null || true

aws iam attach-role-policy \
    --role-name ecsTaskExecutionRole \
    --policy-arn arn:aws:iam::aws:policy/CloudWatchLogsFullAccess 2>/dev/null || true

echo "   ✅ ECS Task Execution Role created"

# Step 4: Create ECS Cluster
echo ""
echo "🚀 Step 4: Creating ECS Cluster..."
aws ecs create-cluster \
    --cluster-name $CLUSTER_NAME \
    --region $AWS_REGION 2>/dev/null || echo "   Cluster already exists"
echo "   ✅ ECS Cluster: $CLUSTER_NAME"

# Step 5: Get Default VPC and Subnets
echo ""
echo "🌐 Step 5: Getting VPC and Subnet information..."
VPC_ID=$(aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" --query "Vpcs[0].VpcId" --output text)
echo "   VPC ID: $VPC_ID"

SUBNET_IDS=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query "Subnets[*].SubnetId" --output text | tr '\t' ',')
echo "   Subnets: $SUBNET_IDS"

# Step 6: Create Security Group for ECS
echo ""
echo "🔒 Step 6: Creating Security Group for ECS..."
SG_ID=$(aws ec2 create-security-group \
    --group-name ecs-catalog-sg \
    --description "ECS Catalog Service Security Group" \
    --vpc-id $VPC_ID \
    --query 'GroupId' \
    --output text 2>/dev/null) || SG_ID=$(aws ec2 describe-security-groups --filters "Name=group-name,Values=ecs-catalog-sg" --query "SecurityGroups[0].GroupId" --output text)

aws ec2 authorize-security-group-ingress \
    --group-id $SG_ID \
    --protocol tcp \
    --port 8000 \
    --cidr 0.0.0.0/0 2>/dev/null || true

echo "   ✅ Security Group: $SG_ID"

# Step 7: Create Task Definition
echo ""
echo "📝 Step 7: Creating ECS Task Definition..."
cat > /tmp/task-definition.json << EOF
{
    "family": "catalog-service-task",
    "networkMode": "awsvpc",
    "requiresCompatibilities": ["FARGATE"],
    "cpu": "256",
    "memory": "512",
    "executionRoleArn": "arn:aws:iam::$AWS_ACCOUNT_ID:role/ecsTaskExecutionRole",
    "containerDefinitions": [
        {
            "name": "catalog-service",
            "image": "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME:latest",
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
                {"name": "LOG_LEVEL", "value": "INFO"},
                {"name": "DATABASE_URL", "value": "sqlite:///./catalog.db"},
                {"name": "JWT_SECRET_KEY", "value": "change-this-in-production"},
                {"name": "AUTH_SERVICE_URL", "value": "http://localhost:8001"},
                {"name": "REDIS_URL", "value": "redis://localhost:6379"},
                {"name": "RABBITMQ_URL", "value": "amqp://guest:guest@localhost:5672/"}
            ],
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-group": "$LOG_GROUP",
                    "awslogs-region": "$AWS_REGION",
                    "awslogs-stream-prefix": "ecs"
                }
            }
        }
    ]
}
EOF

aws ecs register-task-definition \
    --cli-input-json file:///tmp/task-definition.json \
    --region $AWS_REGION > /dev/null
echo "   ✅ Task Definition registered"

# Step 8: Get first two subnets for service
SUBNET1=$(echo $SUBNET_IDS | cut -d',' -f1)
SUBNET2=$(echo $SUBNET_IDS | cut -d',' -f2)

# Step 9: Create ECS Service
echo ""
echo "🎯 Step 8: Creating ECS Service..."
aws ecs create-service \
    --cluster $CLUSTER_NAME \
    --service-name $SERVICE_NAME \
    --task-definition catalog-service-task \
    --desired-count 1 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[$SUBNET1,$SUBNET2],securityGroups=[$SG_ID],assignPublicIp=ENABLED}" \
    --region $AWS_REGION 2>/dev/null || echo "   Service already exists"
echo "   ✅ ECS Service created"

# Summary
echo ""
echo "=============================================="
echo "   ✅ AWS Infrastructure Setup Complete!"
echo "=============================================="
echo ""
echo "Resources Created:"
echo "  • ECR Repository: $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME"
echo "  • ECS Cluster: $CLUSTER_NAME"
echo "  • ECS Service: $SERVICE_NAME"
echo "  • Security Group: $SG_ID"
echo "  • Log Group: $LOG_GROUP"
echo ""
echo "Next Steps:"
echo "  1. Build and push your Docker image to ECR"
echo "  2. The ECS service will start once an image is available"
echo "  3. Configure Jenkins with your AWS Account ID: $AWS_ACCOUNT_ID"
echo ""
echo "=============================================="
