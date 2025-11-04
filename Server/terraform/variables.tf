variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (e.g., dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "ai-admissions-assistant"
}

variable "lambda_zip_path" {
  description = "Path to the Lambda deployment package"
  type        = string
}

variable "lambda_layer_aws_zip_path" {
  description = "Path to the Lambda Layer package containing AWS SDK dependencies"
  type        = string
}

variable "lambda_layer_app_zip_path" {
  description = "Path to the Lambda Layer package containing application dependencies"
  type        = string
}

variable "lambda_layer_scraping_zip_path" {
  description = "Path to the Lambda Layer package containing web scraping dependencies"
  type        = string
}

variable "lambda_layer_arns" {
  description = "List of Lambda Layer ARNs to attach to the function"
  type        = list(string)
  default     = []
}

variable "openai_vector_store_id" {
  description = "OpenAI Vector Store ID"
  type        = string
}