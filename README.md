# serverless-backend
Code for our Backend in AWS Lambda

Built on Python 3.11 as this is a known LST (Long Term Support) Lambda version

# How to deploy

We use SAM for deployment and FastAPI for the ASGI REST API implementation

to deploy to stage:

* Install aws-cli and sam-cli
* Run `sam build`
* Run `sam deploy --guided --config-env stage`
* Accept options and check the deployment. 

This will update the stage-genuis-api function with the latest changes

# How to make changes in DocumentDB

We use an ec2 instance called documentDB-connection, from which we connect to mongo using mongosh. 

Currently, we have a couple collections, `users`, `conversations` and `messages`


# To run locally

## Disable authentication

1. Comment the try except in auth.py
2. Comment the jwt_token param in endpoints in main.py
3. Comment the TLS lines in db.py MongoClient creation in aws/db.py

## Start dummy mongoDB container

`docker run --name my-mongo-db -p 27017:27017 -d mongo:latest`

## Run the project

`$cd src`

`find /Users/mateo/genuis/product-agent-api/src -type d -name "__pycache__" -exec rm -rf {} +`

`$PYTHONPATH=/Users/mateo/genuis/serverless-backend uvicorn main:genuis_api --reload --host 0.0.0.0 --port 8000`

You can replace PYTHONPATH with your own full path to the project


## To run unit tests

### Run specific test classes or methods

  #### Test specific class
  python -m pytest test/test_providers.py:
  :TestOpenAIProvider -v

  #### Test specific method
  python -m pytest
  test/test_providers.py::TestOpenAIProvid
  er::test_completion_no_client -v

  ### Run tests with more detailed output

  #### Show print statements and more details
  python -m pytest test/ -v -s

  #### Show test coverage
  python -m pytest test/ --cov=src

  #### Show only failing tests
  python -m pytest test/ -x

  ### Test the exception changes specifically

  #### Test that exception types are working correctly
  python -m pytest test/test_providers.py
  -k "completion_no_client or 
  completion_api_error" -v


   Individual Test Suites

  1. Database Models Tests

  PYTHONPATH=./src python -m pytest test/core/test_db_models.py -v

  2. Database Utilities Tests

  PYTHONPATH=./src python -m pytest test/aws/test_job_db_utils.py -v

  3. Orchestrator Agent Tools Tests

  PYTHONPATH=./src python -m pytest test/agents/test_orchestrator_tools.py -v

  4. Async API Endpoints Tests

  # Note: These require AUTH0_DOMAIN and API_AUDIENCE environment variables
  AUTH0_DOMAIN=test.auth0.com API_AUDIENCE=test_api PYTHONPATH=./src python -m
   pytest test/api/test_async_endpoints.py -v

  Run All New Tests Together

  # All orchestrator-related tests
  PYTHONPATH=./src python -m pytest test/core/test_db_models.py
  test/aws/test_job_db_utils.py test/agents/test_orchestrator_tools.py -v

  Run Complete Test Suite

  # All tests in the project
  PYTHONPATH=./src python -m pytest test/ -v

  Individual Test Classes/Methods (for debugging)

  # Specific test class
  PYTHONPATH=./src python -m pytest
  test/agents/test_orchestrator_tools.py::TestCheckUserCredits -v

  # Specific test method
  PYTHONPATH=./src python -m pytest test/agents/test_orchestrator_tools.py::Te
  stCheckUserCredits::test_check_user_credits_sufficient_credits -v

  Test Coverage Summary

  - 26 tests for Database Models
  - 17 tests for Database Utilities
  - 20 tests for Orchestrator Agent Tools
  - Additional tests for API Endpoints


  # Prompt engineering

  refer to the best practices as per Anthropic https://www.anthropic.com/engineering/building-effective-agents
  