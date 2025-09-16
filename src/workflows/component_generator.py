import uuid
import xml.etree.ElementTree as ET

from typing import List
from exceptions import LLMProviderCompletionFailedException, SVGInvalidException
from models.request_models import Component
from llm.providers.factory import LLMFactory
from workflows.config.prompts import COMPONENT_GENERATOR_SYSTEM_PROMPT
from logs import logger


class AsyncComponentGenerator:
    def __init__(self, model_name: str, user_prompt: str):
        self.model_name = model_name
        self.system_prompt = COMPONENT_GENERATOR_SYSTEM_PROMPT
        self.user_prompt = user_prompt


    def _validate_svg(self, svg_content: str) -> bool:
        """Validate if the generated content is a valid SVG"""
        try:
            if not svg_content.strip().startswith('<svg'):
                return False

            if not svg_content.strip().endswith('</svg>'):
                return False

            ET.fromstring(svg_content)
            return True

        except ET.ParseError as e:
            logger.error(f"SVG validation failed - XML parse error: {e}")
            return False
        except Exception as e:
            logger.error(f"SVG validation failed: {e}")
            return False

    async def _make_llm_request(self, messages: List) -> str:
        try:
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

        if not self._validate_svg(generated_code):
            logger.error(f"Generated SVG is invalid for prompt: {self.user_prompt[:50]}...")
            raise SVGInvalidException(f"Generated SVG is not valid XML or doesn't follow SVG structure")

        component = Component(
            id=str(uuid.uuid4()),
            code=generated_code
        )

        return component