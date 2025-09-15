import json
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from app import lambda_handler 
from dotenv import load_dotenv 

load_dotenv()

class ResponseModel:
    def __init__(self, status_code, message=None, error=None):
        self.status_code = status_code
        self.message = message
        self.error = error

    def __repr__(self):
        return f"Response(status={self.status_code}, message='{self.message}', error='{self.error}')"

def main():
    print("--- Running Local Lambda Test ---")

    DATABASE_URI = os.environ.get("DATABASE_URI")
    DB_NAME = os.environ.get("DB_NAME", "genuis-db")
    DB_USERNAME = os.environ.get("DB_USERNAME")
    DB_PASSWORD = os.environ.get("DB_PASSWORD")
    
    # --- Step 2: Define the job ID you want to test ---
    # This should be an ID that exists in your local Docker MongoDB instance.
    test_job_id = "1fae8689-174e-4833-88d8-980f2258054e" # Original job ID

    # --- Step 3: Create the mock 'event' object ---
    # This simulates the payload coming from an API Gateway.
    # The 'body' must be a JSON *string*, which is why we use json.dumps().
    mock_event = {
        "body": json.dumps({
            "job_id": test_job_id
        })
    }

    # The 'context' object is often not needed for simple tests and can be None.
    mock_context = None

    # --- Step 4: Invoke the handler function ---
    print(f"Invoking handler with job_id: {test_job_id}")
    result = lambda_handler(mock_event, mock_context)

    # --- Step 5: Print the result ---
    print("\n--- Handler Response ---")
    print(result)
    print("------------------------")


if __name__ == "__main__":
    main()