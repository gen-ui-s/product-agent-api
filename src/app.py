import json
from logs import logger

from main import run


def lambda_handler(event, context):
    try:

        body = event.get("body", event)
        payload = body
        job_id = payload.get('job_id', None)

        if not job_id:
            logger.error("job_id not found in payload")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'job_id is required in the payload.'})
            }

        logger.info(f"Processing job with ID: {job_id}")

        result = run(job_id)
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': f'Generating components for job_id: {job_id}'})
        }

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON payload: {e}")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid JSON format.'})
        }
    except Exception as e:
        logger.error(f"An error occurred in lambda_handler: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal Server Error.'})
        }