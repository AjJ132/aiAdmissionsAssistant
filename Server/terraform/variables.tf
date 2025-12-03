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

variable "openai_assistant_id" {
  description = "OpenAI Assistant ID for chat functionality"
  type        = string
}

variable "scrape_schedule_expression" {
  description = "EventBridge schedule expression for nightly scraping (cron format)"
  type        = string
  default     = "cron(0 0 * * ? *)"  # Default: midnight UTC every day
}

variable "enable_scheduled_scraping" {
  description = "Enable or disable the scheduled scraping EventBridge rule"
  type        = bool
  default     = true
}

# SNS Alerting Variables
variable "enable_scraping_alerts" {
  description = "Enable or disable SNS alerting for scraping failures"
  type        = bool
  default     = true
}

variable "alert_email_addresses" {
  description = "List of email addresses to receive scraping failure alerts"
  type        = list(string)
  default     = []
  sensitive   = true
}

variable "scraping_lambda_timeout_threshold_percentage" {
  description = "Percentage of Lambda timeout duration that triggers alarm"
  type        = number
  default     = 90
  validation {
    condition     = var.scraping_lambda_timeout_threshold_percentage > 0 && var.scraping_lambda_timeout_threshold_percentage <= 100
    error_message = "Threshold percentage must be between 1 and 100"
  }
}
