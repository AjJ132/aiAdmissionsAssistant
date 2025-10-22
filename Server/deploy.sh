#!/bin/bash

set -e  # Exit on any error

echo "=========================================="
echo "AI Admissions Assistant Deployment Script"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="ai-admissions-assistant"
BUILD_DIR="build"
PACKAGE_DIR="${BUILD_DIR}/package"
ZIP_FILE="${BUILD_DIR}/lambda_deployment.zip"

# Clean previous build
echo -e "${YELLOW}Cleaning previous build...${NC}"
rm -rf ${BUILD_DIR}
mkdir -p ${PACKAGE_DIR}

# Install dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
pip install -r requirements.txt -t ${PACKAGE_DIR} --upgrade

# Copy application code
echo -e "${YELLOW}Copying application code...${NC}"
cp handler.py ${PACKAGE_DIR}/
cp -r src ${PACKAGE_DIR}/

# Create deployment package
echo -e "${YELLOW}Creating deployment package...${NC}"
cd ${PACKAGE_DIR}
zip -r ../${ZIP_FILE##*/} . -q
cd ../..

# Get the absolute path of the zip file
ZIP_PATH=$(pwd)/${ZIP_FILE}
echo -e "${GREEN}Deployment package created: ${ZIP_PATH}${NC}"
echo -e "${GREEN}Package size: $(du -h ${ZIP_FILE} | cut -f1)${NC}"

# Run Terraform
echo -e "${YELLOW}Running Terraform...${NC}"
cd terraform

# Initialize Terraform (in case providers need updating)
echo -e "${YELLOW}Initializing Terraform...${NC}"
terraform init

# Plan the deployment
echo -e "${YELLOW}Planning Terraform deployment...${NC}"
terraform plan -var="lambda_zip_path=${ZIP_PATH}"


terraform apply -var="lambda_zip_path=${ZIP_PATH}" -auto-approve

echo -e "${GREEN}=========================================="
echo -e "Deployment completed successfully!"
echo -e "==========================================${NC}"

# Display outputs
echo -e "${GREEN}Deployment Information:${NC}"
terraform output

# Save outputs to file
terraform output -json > ../deployment-info.json
echo -e "${GREEN}Deployment info saved to deployment-info.json${NC}"

fi

cd ..

echo -e "${GREEN}Done!${NC}"
