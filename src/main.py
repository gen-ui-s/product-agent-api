
import asyncio
from typing import List
from datetime import datetime

from aws.db_connection import get_db
from workflows.prompt_generator import PromptGenerator
from workflows.component_generator import AsyncComponentGenerator
from db.job_utils import (
    find_job_by_id,
    find_job_components,
    update_job_status,
    update_job_planning,
    update_component_planning,
    bulk_update_component_status,
    update_component_with_result,
    consume_user_credits
)
from models.db_models import Job, Component
from job_config import JobStatus, ComponentStatus
from llm.providers.factory import LLMFactory, LLMProvider
from exceptions import (
    ComponentGenerationFailedException,
    ComponentGeneratedLengthMismatchException,
    ComponentsNotFoundException,
    ComponentStatusUpdateFailedException,
    JobNotFoundException,
    JobStatusUpdateFailedException,
    PromptGenerationFailedException
)
from logs import logger
import traceback


def generate_component_prompts(job_data: Job) -> List[str]:
    prompt_generator = PromptGenerator(job_data)
    component_prompts = prompt_generator.run()
    return component_prompts


async def _generate_single_component(job_data: Job, prompt: str, provider: LLMProvider) -> Component:
    try:
        component_generator = AsyncComponentGenerator(
            model_name=job_data["model"],
            user_prompt=prompt
        )
        component = await component_generator.generate_component_code(provider)
        component_id = component.id
        logger.info(f"Successful component: {component_id}")
        return component
    
    except Exception as e:
        logger.error(f"Component generation failed. Error: {str(e)}")
        raise ComponentGenerationFailedException(message=str(e), invalid_code=None, sub_prompt=prompt)
    

async def generate_components_concurrently(job_data: Job, component_prompts: List[str]) -> dict:
    logger.info(f"Starting concurrent generation for {len(component_prompts)} prompts for job {job_data['_id']}. ")

    provider = LLMFactory.create_async_provider(job_data["model"])

    tasks = [
        _generate_single_component(job_data, prompt['sub_prompt'], provider)
        for prompt in component_prompts
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results


def save_generation_results_to_db(db, job_components: List[dict], generation_results: List, current_time: str):
    """Save generation results to database and update component statuses"""
    if len(job_components) != len(generation_results):
        raise ComponentGeneratedLengthMismatchException(f"Mismatch between job components ({len(job_components)}) and generation results ({len(generation_results)})")

    successful_component_count = 0

    for db_component, result in zip(job_components, generation_results):
        if isinstance(result, ComponentGenerationFailedException):
            logger.info(f"Updating component {db_component['_id']} as FAILED. Error: {str(result)}")
            update_component_with_result(
                db,
                component_id=db_component['_id'],
                status=ComponentStatus.FAILED,
                code=getattr(result, 'invalid_code', None),
                sub_prompt=getattr(result, 'sub_prompt', None),
                error_message=result.message,
                completed_at=current_time
            )
        else:
            logger.info(f"Updating component {db_component['_id']} as SUCCESSFUL")
            update_component_with_result(
                db,
                component_id=db_component['_id'],
                status=ComponentStatus.SUCCESSFUL,
                code=result.code,
                sub_prompt=getattr(result, 'sub_prompt', None),
                completed_at=current_time
            )
            successful_component_count += 1
        
    return successful_component_count


def run(job_id: str):
    try:
        db = get_db()
        job_data: Job = find_job_by_id(db, job_id)

        update_job_status(db, job_id, JobStatus.RUNNING)
        job_components = find_job_components(db, job_id)
        job_component_ids = [c["_id"] for c in job_components]
        components_prompts: dict = generate_component_prompts(job_data)
        update_job_planning(db, job_id, components_prompts)

        # Update each component with its newly generated sub_prompt and set status to RUNNING
        for db_component, prompt_data in zip(job_components, components_prompts["sub_prompts"]["screens"]):
            update_component_planning(db, db_component["_id"], ComponentStatus.RUNNING, prompt_data["sub_prompt"])

        generation_results: dict = asyncio.run(generate_components_concurrently(job_data, components_prompts["sub_prompts"]["screens"]))

        current_time = datetime.now().isoformat()
        successful_component_count = save_generation_results_to_db(db, job_components, generation_results, current_time)
        update_job_status(db, job_id, JobStatus.COMPLETED, current_time)
        consume_user_credits(db, job_data["user_id"], successful_component_count)

    except (PromptGenerationFailedException, ComponentGeneratedLengthMismatchException) as e:
        logger.info(f"Setting all components as failed. Reason: {e}")
        update_job_status(db, job_id, JobStatus.COMPLETED)
        bulk_update_component_status(db, job_component_ids, ComponentStatus.FAILED)
        return

    except (JobNotFoundException, JobStatusUpdateFailedException, ComponentsNotFoundException, ComponentStatusUpdateFailedException) as e:
        #Don't change  state in case of dabatase errors to protect data integrity.
        logger.error(f"Database error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise e

    except Exception as e:
        logger.error(f"Internal error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise e

