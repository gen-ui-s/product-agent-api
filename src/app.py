import json
from logs import logger
from models.response_models import ResponseModel

from main import run


def lambda_handler(event, context):
    try:
        payload = json.loads(event['body'])
        job_id = payload.get('job_id', None)

        if not job_id:
            logger.error("job_id not found in payload")
            return ResponseModel(
                status_code=400,
                error='job_id is required in the payload.'
            )

        logger.info(f"Processing job with ID: {job_id}")

        result = run(job_id)
        
        return ResponseModel(
            status_code=200,
            message=f'Generating components for job_id: {job_id}'
        )

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON payload: {e}")
        return ResponseModel(
            status_code=400,
            error='Invalid JSON format.'
        )
    except Exception as e:
        logger.error(f"An error occurred in lambda_handler: {e}")
        return ResponseModel(
            status_code=500,
            error='Internal Server Error.'
        )