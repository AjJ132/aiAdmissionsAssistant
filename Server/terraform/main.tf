terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Lambda Layer for AWS SDK dependencies
resource "aws_lambda_layer_version" "aws_sdk_layer" {
  filename            = var.lambda_layer_aws_zip_path
  layer_name          = "${var.project_name}-aws-sdk-${var.environment}"
  compatible_runtimes = ["python3.13"]
  source_code_hash    = filebase64sha256(var.lambda_layer_aws_zip_path)

  description = "AWS SDK dependencies for ${var.project_name}"
}

# Lambda Layer for app dependencies
resource "aws_lambda_layer_version" "app_dependencies_layer" {
  filename            = var.lambda_layer_app_zip_path
  layer_name          = "${var.project_name}-app-dependencies-${var.environment}"
  compatible_runtimes = ["python3.13"]
  source_code_hash    = filebase64sha256(var.lambda_layer_app_zip_path)

  description = "Application dependencies for ${var.project_name}"
}

# Lambda Layer for scraping dependencies
resource "aws_lambda_layer_version" "scraping_dependencies_layer" {
  filename            = var.lambda_layer_scraping_zip_path
  layer_name          = "${var.project_name}-scraping-dependencies-${var.environment}"
  compatible_runtimes = ["python3.13"]
  source_code_hash    = filebase64sha256(var.lambda_layer_scraping_zip_path)

  description = "Web scraping dependencies for ${var.project_name}"
}

# Lambda Function
resource "aws_lambda_function" "api_lambda" {
  filename         = var.lambda_zip_path
  function_name    = "${var.project_name}-${var.environment}"
  role            = aws_iam_role.lambda_role.arn
  handler         = "handler.lambda_handler"
  source_code_hash = filebase64sha256(var.lambda_zip_path)
  runtime         = "python3.13"
  timeout         = 90
  memory_size     = 512

  environment {
    variables = {
      ENVIRONMENT                = var.environment
      OPENAI_API_KEY_SECRET      = "${var.project_name}-openai-api-key-${var.environment}"
      OPENAI_VECTOR_STORE_ID     = var.openai_vector_store_id
      OPENAI_ASSISTANT_ID        = var.openai_assistant_id
    }
  }

  layers = concat([
    aws_lambda_layer_version.aws_sdk_layer.arn,
    aws_lambda_layer_version.app_dependencies_layer.arn,
    aws_lambda_layer_version.scraping_dependencies_layer.arn
  ], var.lambda_layer_arns)

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# IAM Role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "${var.project_name}-lambda-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# Attach basic execution policy
resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# IAM Policy for Secrets Manager access
resource "aws_iam_role_policy" "lambda_secrets_manager" {
  name = "${var.project_name}-lambda-secrets-manager-${var.environment}"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = "arn:aws:secretsmanager:${var.aws_region}:*:secret:${var.project_name}-openai-api-key-${var.environment}-*"
      }
    ]
  })
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "lambda_log_group" {
  name              = "/aws/lambda/${aws_lambda_function.api_lambda.function_name}"
  retention_in_days = 7

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# API Gateway HTTP API
resource "aws_apigatewayv2_api" "http_api" {
  name          = "${var.project_name}-api-${var.environment}"
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins = ["*"]
    allow_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allow_headers = ["content-type", "authorization", "x-amz-date", "x-api-key", "x-amz-security-token"]
    max_age       = 300
  }

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# API Gateway Integration
resource "aws_apigatewayv2_integration" "lambda_integration" {
  api_id           = aws_apigatewayv2_api.http_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.api_lambda.invoke_arn
  integration_method = "POST"
  payload_format_version = "2.0"
}

# API Gateway Routes
resource "aws_apigatewayv2_route" "scrape_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "POST /scrape"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

resource "aws_apigatewayv2_route" "chat_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "POST /chat"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

# API Gateway Stage
resource "aws_apigatewayv2_stage" "default_stage" {
  api_id      = aws_apigatewayv2_api.http_api.id
  name        = "$default"
  auto_deploy = true

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# Lambda Permission for API Gateway
resource "aws_lambda_permission" "api_gateway_invoke" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*"
}

# EventBridge Rule for nightly scraping at midnight UTC
resource "aws_cloudwatch_event_rule" "nightly_scrape" {
  count               = var.enable_scheduled_scraping ? 1 : 0
  name                = "${var.project_name}-nightly-scrape-${var.environment}"
  description         = "Trigger scraping operation every night at midnight UTC"
  schedule_expression = var.scrape_schedule_expression

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# EventBridge Target - Lambda Function
resource "aws_cloudwatch_event_target" "lambda_target" {
  count     = var.enable_scheduled_scraping ? 1 : 0
  rule      = aws_cloudwatch_event_rule.nightly_scrape[0].name
  target_id = "NightlyScrapeTarget"
  arn       = aws_lambda_function.api_lambda.arn

  # Input to trigger the scrape endpoint
  input = jsonencode({
    routeKey = "POST /scrape"
    version  = "2.0"
    rawPath  = "/scrape"
    rawQueryString = ""
    headers = {
      "content-type" = "application/json"
    }
    queryStringParameters = {}
    requestContext = {
      accountId    = "scheduled-event"
      apiId        = "scheduled"
      domainName   = "scheduled.eventbridge"
      domainPrefix = "scheduled"
      http = {
        method   = "POST"
        path     = "/scrape"
        protocol = "HTTP/1.1"
        sourceIp = "0.0.0.0"
        userAgent = "Amazon-EventBridge"
      }
      requestId = "scheduled-request-id"
      stage     = "scheduled"
      time      = "scheduled"
      timeEpoch = 0
    }
    body = jsonencode({})
    isBase64Encoded = false
  })
}

# Lambda Permission for EventBridge
resource "aws_lambda_permission" "eventbridge_invoke" {
  count         = var.enable_scheduled_scraping ? 1 : 0
  statement_id  = "AllowEventBridgeInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.nightly_scrape[0].arn
}
