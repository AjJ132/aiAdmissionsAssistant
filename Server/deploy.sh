#!/bin/bash

# Deploy script for AI Admissions Assistant Lambda
# This script builds the deployment packages and applies Terraform configuration

set -e  # Exit on any error

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$PROJECT_ROOT/terraform"

echo "🚀 Starting deployment process..."
echo "Project root: $PROJECT_ROOT"
echo "Terraform directory: $TERRAFORM_DIR"
echo ""

# Step 1: Run the build script
echo "📦 Step 1: Building deployment packages..."
if [ -f "$PROJECT_ROOT/build.sh" ]; then
    cd "$PROJECT_ROOT"
    ./build.sh
    if [ $? -ne 0 ]; then
        echo "❌ Build failed! Exiting."
        exit 1
    fi
    echo "✅ Build completed successfully"
else
    echo "❌ build.sh not found in $PROJECT_ROOT"
    exit 1
fi

echo ""

# Step 2: Initialize Terraform if needed
echo "🔧 Step 2: Checking Terraform initialization..."
cd "$TERRAFORM_DIR"

if [ ! -d ".terraform" ]; then
    echo "Initializing Terraform..."
    terraform init
    if [ $? -ne 0 ]; then
        echo "❌ Terraform init failed! Exiting."
        exit 1
    fi
    echo "✅ Terraform initialized successfully"
else
    echo "✅ Terraform already initialized"
fi

echo ""

# Step 3: Validate Terraform configuration
echo "🔍 Step 3: Validating Terraform configuration..."
terraform validate
if [ $? -ne 0 ]; then
    echo "❌ Terraform validation failed! Exiting."
    exit 1
fi
echo "✅ Terraform configuration is valid"

echo ""

# Step 4: Plan Terraform deployment (optional, for visibility)
echo "📋 Step 4: Planning Terraform deployment..."
terraform plan -out=tfplan
if [ $? -ne 0 ]; then
    echo "❌ Terraform plan failed! Exiting."
    exit 1
fi
echo "✅ Terraform plan completed"

echo ""

# Step 5: Apply Terraform configuration
echo "🚀 Step 5: Applying Terraform configuration..."
echo "This will create/update AWS resources..."

terraform apply -auto-approve tfplan
if [ $? -ne 0 ]; then
    echo "❌ Terraform apply failed! Exiting."
    exit 1
fi

# Clean up plan file
rm -f tfplan

echo ""
echo "🎉 Deployment completed successfully!"
echo ""

# Display outputs
echo "📊 Deployment Information:"
echo "=========================="
terraform output -json | jq -r 'to_entries[] | "\(.key): \(.value.value)"' 2>/dev/null || terraform output

echo ""
echo "✅ Your AI Admissions Assistant is now deployed!"
echo "🌐 Use the API Gateway URL above to access your application"
echo ""
echo "💡 Useful commands:"
echo "   - View logs: aws logs tail /aws/lambda/\$(terraform output -raw lambda_function_name) --follow"
echo "   - Test endpoint: curl \$(terraform output -raw api_gateway_url)"
echo "   - Destroy resources: terraform destroy"