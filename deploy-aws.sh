#!/bin/bash

# AWS Deployment Script for Catalog Service
# Prerequisites: AWS CLI configured with appropriate credentials

set -e

AWS_REGION="us-east-1"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
SERVICE_NAME="catalog-service"
CLUSTER_NAME="bt-microservices-cluster"

echo "=== AWS Catalog Service Deployment ==="
echo "Account ID: $AWS_ACCOUNT_ID"
echo "Region: $AWS_REGION"

# 1. Create ECR Repository
echo "Step 1: Creating ECR Repository..."
aws ecr create-repository \
    --repository-name $SERVICE_NAME \
    --region $AWS_REGION \
    --image-scanning-configuration scanOnPush=true \
    || echo "ECR repository already exists"

# 2. Create CloudWatch Log Group
echo "Step 2: Creating CloudWatch Log Group..."
aws logs create-log-group \
    --log-group-name /ecs/$SERVICE_NAME \
    --region $AWS_REGION \
    || echo "Log group already exists"

# 3. Create Secrets in AWS Secrets Manager
echo "Step 3: Creating secrets (update with actual values)..."
aws secretsmanager create-secret \
    --name catalog/database-url \
    --secret-string "postgresql://user:pass@host:5432/catalog_db" \
    --region $AWS_REGION \
    || echo "Database secret already exists"

aws secretsmanager create-secret \
    --name catalog/jwt-secret \
    --secret-string "your-jwt-secret-key-change-in-production" \
    --region $AWS_REGION \
    || echo "JWT secret already exists"

aws secretsmanager create-secret \
    --name catalog/redis-url \
    --secret-string "redis://default:pass@host:port" \
    --region $AWS_REGION \
    || echo "Redis secret already exists"

aws secretsmanager create-secret \
    --name catalog/rabbitmq-url \
    --secret-string "amqp://user:pass@host:5672/" \
    --region $AWS_REGION \
    || echo "RabbitMQ secret already exists"

# 4. Create VPC and Subnets (if not exists)
echo "Step 4: Setting up VPC..."
VPC_ID=$(aws ec2 describe-vpcs --filters "Name=tag:Name,Values=bt-microservices-vpc" --query "Vpcs[0].VpcId" --output text --region $AWS_REGION)

if [ "$VPC_ID" == "None" ]; then
    echo "Creating VPC..."
    VPC_ID=$(aws ec2 create-vpc --cidr-block 10.0.0.0/16 --region $AWS_REGION --query 'Vpc.VpcId' --output text)
    aws ec2 create-tags --resources $VPC_ID --tags Key=Name,Value=bt-microservices-vpc --region $AWS_REGION
    
    # Create subnets
    SUBNET1=$(aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.1.0/24 --availability-zone ${AWS_REGION}a --query 'Subnet.SubnetId' --output text)
    SUBNET2=$(aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.2.0/24 --availability-zone ${AWS_REGION}b --query 'Subnet.SubnetId' --output text)
    
    # Create Internet Gateway
    IGW_ID=$(aws ec2 create-internet-gateway --query 'InternetGateway.InternetGatewayId' --output text)
    aws ec2 attach-internet-gateway --vpc-id $VPC_ID --internet-gateway-id $IGW_ID
    
    echo "VPC created: $VPC_ID"
else
    echo "Using existing VPC: $VPC_ID"
fi

# 5. Create Security Group
echo "Step 5: Creating Security Group..."
SG_ID=$(aws ec2 create-security-group \
    --group-name ${SERVICE_NAME}-sg \
    --description "Security group for catalog service" \
    --vpc-id $VPC_ID \
    --region $AWS_REGION \
    --query 'GroupId' \
    --output text) || echo "Security group may already exist"

aws ec2 authorize-security-group-ingress \
    --group-id $SG_ID \
    --protocol tcp \
    --port 8000 \
    --cidr 0.0.0.0/0 \
    --region $AWS_REGION \
    || echo "Ingress rule already exists"

# 6. Create ECS Cluster
echo "Step 6: Creating ECS Cluster..."
aws ecs create-cluster \
    --cluster-name $CLUSTER_NAME \
    --region $AWS_REGION \
    || echo "Cluster already exists"

# 7. Register Task Definition
echo "Step 7: Registering ECS Task Definition..."
sed "s/<AWS_ACCOUNT_ID>/$AWS_ACCOUNT_ID/g" ecs-task-definition.json > ecs-task-definition-updated.json
aws ecs register-task-definition \
    --cli-input-json file://ecs-task-definition-updated.json \
    --region $AWS_REGION

# 8. Create Application Load Balancer
echo "Step 8: Creating Application Load Balancer..."
ALB_ARN=$(aws elbv2 create-load-balancer \
    --name ${SERVICE_NAME}-alb \
    --subnets $SUBNET1 $SUBNET2 \
    --security-groups $SG_ID \
    --region $AWS_REGION \
    --query 'LoadBalancers[0].LoadBalancerArn' \
    --output text) || echo "ALB may already exist"

# Get ALB DNS
ALB_DNS=$(aws elbv2 describe-load-balancers \
    --names ${SERVICE_NAME}-alb \
    --region $AWS_REGION \
    --query 'LoadBalancers[0].DNSName' \
    --output text)

# 9. Create Target Group
echo "Step 9: Creating Target Group..."
TG_ARN=$(aws elbv2 create-target-group \
    --name ${SERVICE_NAME}-tg \
    --protocol HTTP \
    --port 8000 \
    --vpc-id $VPC_ID \
    --target-type ip \
    --health-check-path /health \
    --region $AWS_REGION \
    --query 'TargetGroups[0].TargetGroupArn' \
    --output text) || echo "Target group may already exist"

# 10. Create Listener
echo "Step 10: Creating ALB Listener..."
aws elbv2 create-listener \
    --load-balancer-arn $ALB_ARN \
    --protocol HTTP \
    --port 80 \
    --default-actions Type=forward,TargetGroupArn=$TG_ARN \
    --region $AWS_REGION \
    || echo "Listener may already exist"

# 11. Create ECS Service
echo "Step 11: Creating ECS Service..."
aws ecs create-service \
    --cluster $CLUSTER_NAME \
    --service-name $SERVICE_NAME \
    --task-definition ${SERVICE_NAME}-task \
    --desired-count 2 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[$SUBNET1,$SUBNET2],securityGroups=[$SG_ID],assignPublicIp=ENABLED}" \
    --load-balancers "targetGroupArn=$TG_ARN,containerName=$SERVICE_NAME,containerPort=8000" \
    --region $AWS_REGION \
    || echo "Service may already exist"

echo ""
echo "=== Deployment Complete ==="
echo "Service URL: http://$ALB_DNS"
echo "Health Check: http://$ALB_DNS/health"
echo "API Docs: http://$ALB_DNS/docs"
echo ""
echo "Note: It may take 2-3 minutes for the service to become healthy"
