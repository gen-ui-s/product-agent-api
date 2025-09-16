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
    

    test_job_id = "put job id here" # Original job ID

    mock_event = {
        "body": json.dumps({
            "job_id": test_job_id
        })
    }

    mock_context = None

    print(f"Invoking handler with job_id: {test_job_id}")
    result = lambda_handler(mock_event, mock_context)

    print("\n--- Handler Response ---")
    print(result)
    print("------------------------")


if __name__ == "__main__":
    main()