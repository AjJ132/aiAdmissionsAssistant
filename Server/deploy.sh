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

# Setup virtual environment
if [ -d "venv" ]; then
    echo -e "${YELLOW}Activating existing virtual environment...${NC}"
    source venv/bin/activate
elif [ -d "../venv" ]; then
    echo -e "${YELLOW}Activating existing virtual environment...${NC}"
    source ../venv/bin/activate
else
    echo -e "${YELLOW}Creating new virtual environment...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    echo -e "${YELLOW}Installing dependencies in virtual environment...${NC}"
    pip install --upgrade pip
    pip install -r requirements.txt
fi

# Configuration
PROJECT_NAME="ai-admissions-assistant"
BUILD_DIR="build"
PACKAGE_DIR="${BUILD_DIR}/package"
ZIP_FILE="${BUILD_DIR}/lambda_deployment.zip"
AWS_LAYER_ZIP="${BUILD_DIR}/lambda_layer_aws.zip"
APP_LAYER_ZIP="${BUILD_DIR}/lambda_layer_app.zip"
SCRAPING_LAYER_ZIP="${BUILD_DIR}/lambda_layer_scraping.zip"

# Clean previous build
echo -e "${YELLOW}Cleaning previous build...${NC}"
rm -rf ${BUILD_DIR}
mkdir -p ${PACKAGE_DIR}

# Build Lambda Layer (dependencies only)
echo -e "${YELLOW}Building Lambda Layer with dependencies...${NC}"
./build_layer.sh

# Copy application code only (no dependencies)
echo -e "${YELLOW}Copying application code...${NC}"
cp handler.py ${PACKAGE_DIR}/
cp -r src ${PACKAGE_DIR}/

# Create deployment package
echo -e "${YELLOW}Creating deployment package...${NC}"
cd ${PACKAGE_DIR}
zip -r ../${ZIP_FILE##*/} . -q
cd ../..

# Get the absolute path of the zip files
ZIP_PATH=$(pwd)/${ZIP_FILE}
AWS_LAYER_ZIP_PATH=$(pwd)/${AWS_LAYER_ZIP}
APP_LAYER_ZIP_PATH=$(pwd)/${APP_LAYER_ZIP}
SCRAPING_LAYER_ZIP_PATH=$(pwd)/${SCRAPING_LAYER_ZIP}
echo -e "${GREEN}Deployment package created: ${ZIP_PATH}${NC}"
echo -e "${GREEN}Package size: $(du -h ${ZIP_FILE} | cut -f1)${NC}"
echo -e "${GREEN}AWS Layer package created: ${AWS_LAYER_ZIP_PATH}${NC}"
echo -e "${GREEN}AWS Layer size: $(du -h ${AWS_LAYER_ZIP} | cut -f1)${NC}"
echo -e "${GREEN}App Layer package created: ${APP_LAYER_ZIP_PATH}${NC}"
echo -e "${GREEN}App Layer size: $(du -h ${APP_LAYER_ZIP} | cut -f1)${NC}"
echo -e "${GREEN}Scraping Layer package created: ${SCRAPING_LAYER_ZIP_PATH}${NC}"
echo -e "${GREEN}Scraping Layer size: $(du -h ${SCRAPING_LAYER_ZIP} | cut -f1)${NC}"

# Run Terraform
echo -e "${YELLOW}Running Terraform...${NC}"
cd terraform

# Initialize Terraform (in case providers need updating)
echo -e "${YELLOW}Initializing Terraform...${NC}"
terraform init

# Plan the deployment
echo -e "${YELLOW}Planning Terraform deployment...${NC}"
terraform plan -var="lambda_zip_path=${ZIP_PATH}" -var="lambda_layer_aws_zip_path=${AWS_LAYER_ZIP_PATH}" -var="lambda_layer_app_zip_path=${APP_LAYER_ZIP_PATH}" -var="lambda_layer_scraping_zip_path=${SCRAPING_LAYER_ZIP_PATH}"


terraform apply -var="lambda_zip_path=${ZIP_PATH}" -var="lambda_layer_aws_zip_path=${AWS_LAYER_ZIP_PATH}" -var="lambda_layer_app_zip_path=${APP_LAYER_ZIP_PATH}" -var="lambda_layer_scraping_zip_path=${SCRAPING_LAYER_ZIP_PATH}" -auto-approve

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
