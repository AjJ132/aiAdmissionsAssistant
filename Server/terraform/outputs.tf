output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = aws_lambda_function.api_lambda.function_name
}

output "lambda_function_arn" {
  description = "ARN of the Lambda function"
  value       = aws_lambda_function.api_lambda.arn
}

output "api_gateway_url" {
  description = "URL of the API Gateway"
  value       = aws_apigatewayv2_api.http_api.api_endpoint
}

output "api_gateway_id" {
  description = "ID of the API Gateway"
  value       = aws_apigatewayv2_api.http_api.id
}

output "scrape_endpoint" {
  description = "Full URL for the scrape endpoint"
  value       = "${aws_apigatewayv2_api.http_api.api_endpoint}/scrape"
}

output "chat_endpoint" {
  description = "Full URL for the chat endpoint"
  value       = "${aws_apigatewayv2_api.http_api.api_endpoint}/chat"
}

output "cloudwatch_log_group" {
  description = "CloudWatch Log Group for Lambda logs"
  value       = aws_cloudwatch_log_group.lambda_log_group.name
}

output "lambda_layers" {
  description = "Lambda layers attached to the function"
  value       = aws_lambda_function.api_lambda.layers
}

output "eventbridge_rule_name" {
  description = "Name of the EventBridge rule for nightly scraping"
  value       = var.enable_scheduled_scraping ? aws_cloudwatch_event_rule.nightly_scrape[0].name : "Disabled"
}

output "eventbridge_rule_arn" {
  description = "ARN of the EventBridge rule for nightly scraping"
  value       = var.enable_scheduled_scraping ? aws_cloudwatch_event_rule.nightly_scrape[0].arn : "Disabled"
}

output "eventbridge_schedule" {
  description = "Schedule expression for the nightly scrape"
  value       = var.enable_scheduled_scraping ? aws_cloudwatch_event_rule.nightly_scrape[0].schedule_expression : "Disabled"
}

# SNS Alerting Outputs
output "scraping_alerts_sns_topic_arn" {
  description = "ARN of SNS topic for scraping alerts"
  value       = var.enable_scraping_alerts ? aws_sns_topic.scraping_alerts[0].arn : "Disabled"
}

output "scraping_alerts_enabled" {
  description = "Whether scraping alerts are enabled"
  value       = var.enable_scraping_alerts
}
