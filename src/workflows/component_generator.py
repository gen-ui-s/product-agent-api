import uuid

from typing import List
from exceptions import LLMProviderCompletionFailedException
from models.request_models import Component
from llm.providers.factory import LLMFactory
from workflows.config.prompts import COMPONENT_GENERATOR_SYSTEM_PROMPT
from logs import logger


class AsyncComponentGenerator:
    def __init__(self, model_name: str, user_prompt: str):
        self.model_name = model_name
        self.system_prompt = COMPONENT_GENERATOR_SYSTEM_PROMPT
        self.user_prompt = user_prompt


    async def _make_llm_request(self, messages: List) -> str:
        try:
            logger.info(f"Making LLM request with model: {self.model_name}")
            provider = LLMFactory.create_async_provider(self.model_name)
            model_response = await provider.completion(
                messages=messages
            )
            
        except Exception as e:
            logger.error(f"LLM API request failed: {str(e)}")
            raise LLMProviderCompletionFailedException(f"LLM API request failed: {str(e)}")
        
        return model_response

    
    async def generate_component_code(self) -> str:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": self.user_prompt}
        ]
        
        generated_code = await self._make_llm_request(messages)

        #TODO check svg is valid and return error if not. 
        component = Component(
            id=str(uuid.uuid4()),
            code=generated_code
        )

        return component