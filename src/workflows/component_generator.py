import uuid
import json
import xml.etree.ElementTree as ET

from typing import List
from exceptions import LLMProviderCompletionFailedException
from models.request_models import Component
from llm.providers.factory import LLMProvider
from workflows.config.prompts import COMPONENT_GENERATOR_SYSTEM_PROMPT
from logs import logger


class AsyncComponentGenerator:
    def __init__(self, model_name: str, user_prompt: str):
        self.model_name = model_name
        self.system_prompt = COMPONENT_GENERATOR_SYSTEM_PROMPT
        self.user_prompt = user_prompt


    async def _make_llm_request(self, messages: List, provider: LLMProvider) -> str:
        try:
            model_response = await provider.completion(
                messages=messages
            )

        except Exception as e:
            logger.error(f"LLM API request failed: {str(e)}")
            raise LLMProviderCompletionFailedException(f"LLM API request failed: {str(e)}")

        return model_response

    
    async def generate_component_code(self, provider: LLMProvider) -> Component:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": self.user_prompt}
        ]

        generated_code = await self._make_llm_request(messages, provider)

        if not generated_code:
            logger.error("Empty LLM Response")
            raise Exception("Empty LLM Response")

        try:
            parsed_json = json.loads(generated_code)
            normalized_code = json.dumps(parsed_json, separators=(',', ':'), ensure_ascii=False)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON for normalization: {str(e)}, using raw response")
            normalized_code = generated_code

        component = Component(
            id=str(uuid.uuid4()),
            code=normalized_code
        )

        return component