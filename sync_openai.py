import os
import openai
from openai import OpenAI

# Initialize the OpenAI client using the secret environment variable
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Replace with your actual Vector Store ID
VECTOR_STORE_ID = "vs_68d65318286081918f95b216ba55ab11" 
FILES_DIR = "scraped_degrees/"

def upload_file_to_vector_store(file_path):
    print(f"Uploading file: {file_path}")
    try:
        with open(file_path, "rb") as f:
            # Upload the file to OpenAI with the purpose "assistants"
            uploaded_file = client.files.create(file=f, purpose="assistants")
            print(f"File uploaded with ID: {uploaded_file.id}")

            # Add the uploaded file to the vector store
            client.beta.vector_stores.files.create(
                vector_store_id=VECTOR_STORE_ID,
                file_id=uploaded_file.id
            )
            print(f"File {uploaded_file.id} added to vector store {VECTOR_STORE_ID}")
    except Exception as e:
        print(f"Error uploading file {file_path}: {e}")

if __name__ == "__main__":
    if not os.path.exists(FILES_DIR):
        print(f"Directory not found: {FILES_DIR}")
    else:
        for filename in os.listdir(FILES_DIR):
            file_path = os.path.join(FILES_DIR, filename)
            if os.path.isfile(file_path):
                # Basic check: in a production system, you'd manage file IDs/checksums
                # to avoid re-uploading the same file on every run.
                upload_file_to_vector_store(file_path)

