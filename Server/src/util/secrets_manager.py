"""
Utility for fetching secrets from AWS Secrets Manager
"""
import os
import json
import boto3
from functools import lru_cache
from botocore.exceptions import ClientError


@lru_cache(maxsize=1)
def get_secret(secret_name: str) -> str:
    """
    Fetch a secret from AWS Secrets Manager.
    Results are cached to avoid repeated API calls.
    
    Args:
        secret_name: The name or ARN of the secret
        
    Returns:
        The secret value as a string
        
    Raises:
        ClientError: If the secret cannot be retrieved
    """
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager')
    
    try:
        response = client.get_secret_value(SecretId=secret_name)
        
        # Secrets can be stored as either SecretString or SecretBinary
        if 'SecretString' in response:
            return response['SecretString']
        else:
            # For binary secrets, decode base64
            import base64
            return base64.b64decode(response['SecretBinary']).decode('utf-8')
            
    except ClientError as e:
        raise Exception(f"Error retrieving secret {secret_name}: {str(e)}")


def get_openai_api_key() -> str:
    """
    Get the OpenAI API key from environment variable or Secrets Manager.
    
    Returns:
        The OpenAI API key
    """
    # Check if running locally with direct env var (highest priority)
    api_key = os.environ.get('OPENAI_API_KEY')
    if api_key:
        return api_key
    
    # In AWS Lambda, get the secret name from env var and fetch from Secrets Manager
    secret_name = os.environ.get('OPENAI_API_KEY_SECRET')
    if secret_name:
        return get_secret(secret_name)
    
    # If neither is set, raise an error
    raise ValueError(
        "OpenAI API key not configured. Set either OPENAI_API_KEY environment variable "
        "for local development, or OPENAI_API_KEY_SECRET for AWS Lambda."
    )
