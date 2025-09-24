#!/bin/bash

# Build script for AWS Lambda deployment
# This script packages Python dependencies into a Lambda layer and prepares the function code

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DIST_DIR="$PROJECT_ROOT/dist"
PYTHON_DIR="$DIST_DIR/python"

echo "🚀 Starting Lambda build process..."

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf "$DIST_DIR"
mkdir -p "$DIST_DIR"
mkdir -p "$PYTHON_DIR"

# Install Python dependencies into the layer
echo "📦 Installing Python dependencies..."
if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
    pip3 install -r "$PROJECT_ROOT/requirements.txt" -t "$PYTHON_DIR" --no-deps
    
    # Install dependencies with their dependencies
    pip3 install -r "$PROJECT_ROOT/requirements.txt" -t "$PYTHON_DIR"
    
    echo "✅ Dependencies installed successfully"
else
    echo "⚠️  No requirements.txt found, skipping dependency installation"
fi

# Remove unnecessary files from the layer to reduce size
echo "🗑️  Removing unnecessary files to reduce layer size..."
find "$PYTHON_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$PYTHON_DIR" -type d -name "*.dist-info" -exec rm -rf {} + 2>/dev/null || true
find "$PYTHON_DIR" -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
find "$PYTHON_DIR" -name "*.pyc" -delete 2>/dev/null || true
find "$PYTHON_DIR" -name "*.pyo" -delete 2>/dev/null || true
find "$PYTHON_DIR" -name "*.pyd" -delete 2>/dev/null || true
find "$PYTHON_DIR" -name ".DS_Store" -delete 2>/dev/null || true

# Create a simple Lambda handler if it doesn't exist
if [ ! -f "$PROJECT_ROOT/handler.py" ]; then
    echo "⚠️  No handler.py found, creating a basic one..."
    cat > "$PROJECT_ROOT/handler.py" << 'EOF'
import json

def lambda_handler(event, context):
    """
    Basic Lambda handler for AI Admissions Assistant
    """
    
    # Handle API Gateway events
    if 'httpMethod' in event:
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            },
            'body': json.dumps({
                'message': 'AI Admissions Assistant API is running!',
                'method': event.get('httpMethod'),
                'path': event.get('path')
            })
        }
    
    # Handle direct invocation
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'AI Admissions Assistant Lambda is running!',
            'event': event
        })
    }
EOF
    echo "✅ Created basic handler.py"
fi

# Create deployment package for Lambda function (excluding dependencies - they're in the layer)
echo "📦 Creating Lambda function package..."
cd "$PROJECT_ROOT"
zip -r "$DIST_DIR/lambda_function.zip" . \
    -x "terraform/*" \
    -x "dist/*" \
    -x "__pycache__/*" \
    -x "*.pyc" \
    -x "*.pyo" \
    -x "*.pyd" \
    -x ".git/*" \
    -x ".gitignore" \
    -x "*.md" \
    -x "build.sh" \
    -x "*.drawio" \
    -x "debug_*.html"

# Create dependencies package for Lambda layer
echo "📦 Creating dependencies layer package..."
cd "$PYTHON_DIR"
zip -r "$DIST_DIR/dependencies.zip" .

cd "$PROJECT_ROOT"

# Display package sizes
echo "📊 Package sizes:"
ls -lh "$DIST_DIR"/*.zip

echo "✅ Build completed successfully!"
echo ""
echo "Next steps:"
echo "1. Navigate to the terraform directory: cd terraform"
echo "2. Initialize Terraform: terraform init"
echo "3. Plan deployment: terraform plan"
echo "4. Deploy: terraform apply"
echo ""
echo "🎉 Ready for deployment!"