from openai import OpenAI
import os

from src.util.secrets_manager import get_openai_api_key
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
VECTOR_STORE_ID = os.environ.get('OPENAI_VECTOR_STORE_ID')

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set")
if not VECTOR_STORE_ID:
    raise ValueError("VECTOR_STORE_ID environment variable is not set")

client = OpenAI(api_key=OPENAI_API_KEY)

# Step 1: Create ONE assistant (do this once)
assistant = client.beta.assistants.create(
    name="Admissions Assistant",
    instructions="You are an admissions advisor. Answer questions about degree programs based on the uploaded data.",
    model="gpt-4o",
    tools=[{"type": "file_search"}],
    tool_resources={
        "file_search": {
            "vector_store_ids": [VECTOR_STORE_ID]  # Your vector store ID
        }
    }
)


ASSISTANT_ID = assistant.id 
print(f"Assistant created with ID: {ASSISTANT_ID}")