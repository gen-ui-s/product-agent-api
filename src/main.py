
import asyncio
from typing import List
from datetime import datetime

from aws.db_connection import get_db
from models.request_models import Component
from workflows.prompt_generator import PromptGenerator
from workflows.component_generator import AsyncComponentGenerator
from db.job_utils import find_job_by_id, find_job_components, update_job_status, update_component_status, update_component_with_result
from models.db_models import Job, Component
from job_config import JobStatus, ComponentStatus
from exceptions import ComponentGenerationFailedException
from logs import logger
import traceback


def generate_component_prompts(job_data: Job) -> List[str]:
    prompt_generator = PromptGenerator(job_data)
    component_prompts = prompt_generator.run()
    return component_prompts["screens"]


async def _generate_single_component(job_data: Job, prompt: str) -> Component:
    try:
        component_generator = AsyncComponentGenerator(
            model_name=job_data["model"],
            user_prompt=prompt
        )
        component = await component_generator.generate_component_code()
        logger.info(f"Successfully generated component for prompt: {prompt[:50]}...")
        return component
    except Exception as e:
        logger.error(f"Failed to generate component for prompt '{prompt[:50]}...': {e}")

        return ComponentGenerationFailedException(f"Failed to generate component: {e}")

async def generate_components_concurrently(job_data: Job, component_prompts: List[str]) -> dict:
    logger.info(f"Starting concurrent generation... for {len(component_prompts)} prompts for job {job_data['_id']}. ")

    logger.info(f"Component Prompts: {component_prompts}")
    tasks = [
        _generate_single_component(job_data, prompt['sub_prompt'])
        for prompt in component_prompts
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    successful_components = []
    failed_components = []

    for result in results:
        if isinstance(result, Exception):
            failed_components.append(result)
        elif isinstance(result, ComponentGenerationFailedException):
            failed_components.append(result)
        elif result is not None:
            successful_components.append(result)

    logger.info(f"Generated {len(successful_components)} successful components, {len(failed_components)} failed")

    return {
        'successful': successful_components,
        'failed': failed_components
    }


def save_generation_results_to_db(db, job_components: List[dict], successful_components: List[Component], failed_components: List[Exception]):
    """Save generation results to database and update component statuses"""
    current_time = datetime.now().isoformat()

    for i, component in enumerate(successful_components):
        if i < len(job_components):
            db_component = job_components[i]
            logger.info(f"Updating component {db_component['_id']} as SUCCESSFUL")
            update_component_with_result(
                db,
                db_component['_id'],
                ComponentStatus.SUCCESSFUL,
                code=component.code,
                completed_at=current_time
            )

    successful_count = len(successful_components)
    for i, error in enumerate(failed_components):
        component_idx = successful_count + i
        if component_idx < len(job_components):
            db_component = job_components[component_idx]
            error_message = str(error) if isinstance(error, Exception) else "Unknown error"
            logger.info(f"Updating component {db_component['_id']} as FAILED: {error_message}")
            update_component_with_result(
                db,
                db_component['_id'],
                ComponentStatus.FAILED,
                error_message=error_message
            )

def run(job_id: str):
    try:
        db = get_db()
        job_data: Job = find_job_by_id(db, job_id)

        update_job_status(db, job_id, JobStatus.RUNNING)
        job_components = find_job_components(db, job_id)
        for component in job_components:
            update_component_status(db, component['_id'], ComponentStatus.RUNNING)

        components_prompts: List[str] = generate_component_prompts(job_data)
        generation_results: dict = asyncio.run(generate_components_concurrently(job_data, components_prompts))

        successful_components = generation_results['successful']
        failed_components = generation_results['failed']

        save_generation_results_to_db(db, job_components, successful_components, failed_components)
        update_job_status(db, job_id, JobStatus.COMPLETED)
        logger.info(f"Job {job_id} completed with {len(successful_components)} successful and {len(failed_components)} failed components")

        return {
            'successful': successful_components,
            'failed': failed_components
        }

    except Exception as e:
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise e
