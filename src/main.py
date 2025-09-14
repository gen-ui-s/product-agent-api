
import asyncio
from typing import List

from aws.db_connection import get_db
from models.request_models import Component
from workflows.prompt_generator import PromptGenerator
from workflows.component_generator import AsyncComponentGenerator
from db.job_utils import find_job_by_id
from models.db_models import Job, Component
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

        return ComponentGenerationFailedException(f"Failed to generate component: {e}") #TODO return error component

async def generate_components_concurrently(job_data: Job, component_prompts: List[str]) -> List[Component]:
    logger.info(f"Starting concurrent generation... for {len(component_prompts)} prompts for job {job_data['_id']}. ")

    logger.info(f"Component Prompts: {component_prompts}")
    tasks = [
        _generate_single_component(job_data, prompt['sub_prompt'])
        for prompt in component_prompts
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    generated_components = [res for res in results if res is not None]
    
    logger.info(f"Generated components: {generated_components}")
    return generated_components


def run(job_id: str):
    try:
        db = get_db()
        
        job_data: Job = find_job_by_id(db, job_id)
        #TODO handle job update stautus
        logger.info(f"Successfully retrieved job data for job_id: {job_data}")
        from llm.config.models import LLMAvailableModels
        job_data["model"] = LLMAvailableModels.GEMINI_2_5_PRO.value.name
        components_prompts: List[str] = generate_component_prompts(job_data)
        components_generated: List[Component] = asyncio.run(generate_components_concurrently(job_data,components_prompts))
        #TODO  Save results in DB

    except Exception as e:
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise e

    return  job_data
