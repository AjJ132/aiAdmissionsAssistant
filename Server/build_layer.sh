#!/bin/bash

set -e  # Exit on any error

echo "=========================================="
echo "Building Lambda Layer"
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
BUILD_DIR="build"
AWS_LAYER_DIR="${BUILD_DIR}/aws_layer"
APP_LAYER_DIR="${BUILD_DIR}/app_layer"
SCRAPING_LAYER_DIR="${BUILD_DIR}/scraping_layer"
AWS_PYTHON_DIR="${AWS_LAYER_DIR}/python/lib/python3.13/site-packages"
APP_PYTHON_DIR="${APP_LAYER_DIR}/python/lib/python3.13/site-packages"
SCRAPING_PYTHON_DIR="${SCRAPING_LAYER_DIR}/python/lib/python3.13/site-packages"
AWS_LAYER_ZIP="${BUILD_DIR}/lambda_layer_aws.zip"
APP_LAYER_ZIP="${BUILD_DIR}/lambda_layer_app.zip"
SCRAPING_LAYER_ZIP="${BUILD_DIR}/lambda_layer_scraping.zip"

# Clean previous layer builds
echo -e "${YELLOW}Cleaning previous layer builds...${NC}"
rm -rf ${AWS_LAYER_DIR} ${APP_LAYER_DIR} ${SCRAPING_LAYER_DIR}
rm -f ${AWS_LAYER_ZIP} ${APP_LAYER_ZIP} ${SCRAPING_LAYER_ZIP}

# Build AWS Layer
echo -e "${YELLOW}=========================================${NC}"
echo -e "${YELLOW}Building AWS SDK Layer...${NC}"
echo -e "${YELLOW}=========================================${NC}"
mkdir -p ${AWS_PYTHON_DIR}

echo -e "${YELLOW}Installing AWS dependencies to layer...${NC}"
pip install -r requirements-aws.txt -t ${AWS_PYTHON_DIR} --upgrade --platform manylinux2014_x86_64 --only-binary=:all: || \
pip install -r requirements-aws.txt -t ${AWS_PYTHON_DIR} --upgrade

echo -e "${YELLOW}Creating AWS layer zip file...${NC}"
cd ${AWS_LAYER_DIR}
zip -r ../${AWS_LAYER_ZIP##*/} . -q
cd ../..

AWS_LAYER_ZIP_PATH=$(pwd)/${AWS_LAYER_ZIP}
echo -e "${GREEN}AWS Lambda Layer created: ${AWS_LAYER_ZIP_PATH}${NC}"
echo -e "${GREEN}AWS Layer size: $(du -h ${AWS_LAYER_ZIP} | cut -f1)${NC}"

# Build App Dependencies Layer
echo -e "${YELLOW}=========================================${NC}"
echo -e "${YELLOW}Building App Dependencies Layer...${NC}"
echo -e "${YELLOW}=========================================${NC}"
mkdir -p ${APP_PYTHON_DIR}

echo -e "${YELLOW}Installing app dependencies to layer...${NC}"
pip install -r requirements-app.txt -t ${APP_PYTHON_DIR} --upgrade --platform manylinux2014_x86_64 --only-binary=:all: || \
pip install -r requirements-app.txt -t ${APP_PYTHON_DIR} --upgrade

echo -e "${YELLOW}Creating app layer zip file...${NC}"
cd ${APP_LAYER_DIR}
zip -r ../${APP_LAYER_ZIP##*/} . -q
cd ../..

APP_LAYER_ZIP_PATH=$(pwd)/${APP_LAYER_ZIP}
echo -e "${GREEN}App Lambda Layer created: ${APP_LAYER_ZIP_PATH}${NC}"
echo -e "${GREEN}App Layer size: $(du -h ${APP_LAYER_ZIP} | cut -f1)${NC}"

# Build Scraping Dependencies Layer
echo -e "${YELLOW}=========================================${NC}"
echo -e "${YELLOW}Building Scraping Dependencies Layer...${NC}"
echo -e "${YELLOW}=========================================${NC}"
mkdir -p ${SCRAPING_PYTHON_DIR}

echo -e "${YELLOW}Installing scraping dependencies to layer...${NC}"
pip install -r requirements-scraping.txt -t ${SCRAPING_PYTHON_DIR} --upgrade --platform manylinux2014_x86_64 --only-binary=:all: || \
pip install -r requirements-scraping.txt -t ${SCRAPING_PYTHON_DIR} --upgrade

echo -e "${YELLOW}Creating scraping layer zip file...${NC}"
cd ${SCRAPING_LAYER_DIR}
zip -r ../${SCRAPING_LAYER_ZIP##*/} . -q
cd ../..

SCRAPING_LAYER_ZIP_PATH=$(pwd)/${SCRAPING_LAYER_ZIP}
echo -e "${GREEN}Scraping Lambda Layer created: ${SCRAPING_LAYER_ZIP_PATH}${NC}"
echo -e "${GREEN}Scraping Layer size: $(du -h ${SCRAPING_LAYER_ZIP} | cut -f1)${NC}"

echo -e "${GREEN}Done!${NC}"
