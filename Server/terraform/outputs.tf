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
