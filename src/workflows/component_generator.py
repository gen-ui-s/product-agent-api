import uuid
import json
import xml.etree.ElementTree as ET

from typing import List, Optional, Dict
from exceptions import LLMProviderCompletionFailedException
from models.request_models import Component
from llm.providers.factory import LLMProvider
from workflows.prompts.component_gen import JSON_UI_GENERATOR_SYSTEM_PROMPT
from workflows.prompts.general import JSON_RULES_SNIPPET, UX_LAWS_SNIPPET
from job_config import AvailableDeviceSizes, DeviceSize
from logs import logger


class AsyncComponentGenerator:
    def __init__(self, model_name: str, user_prompt: str):
        self.model_name = model_name
        # Note: We delay prompt formatting to the generate call where we have all context
        self.base_system_prompt = JSON_UI_GENERATOR_SYSTEM_PROMPT
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

    
    async def generate_component_code(
        self, 
        provider: LLMProvider, 
        device_name: str = "Desktop",
        ia_context: Optional[Dict] = None
    ) -> Component:
        
        # 1. Resolve Device Size
        try:
            device_enum = AvailableDeviceSizes.get_device_by_name(device_name)
            device_size = device_enum  # This is the DeviceSize object
        except ValueError:
            # Fallback if unknown
            device_size = DeviceSize(width=1440, height=1024, corner_radius=0, name="Desktop")
            logger.warning(f"Device '{device_name}' not found, defaulting to Desktop.")

        # 2. Format Device Specs (JSON)
        device_specs_str = json.dumps({
            "target_device": device_size.name,
            "width": device_size.width,
            "height": device_size.height,
            "corner_radius": device_size.corner_radius
        }, indent=2)

        # 3. Format System Prompt with Snippets and Device Info
        formatted_system_prompt = self.base_system_prompt.format(
            JSON_RULES_SNIPPET=JSON_RULES_SNIPPET,
            UX_LAWS_SNIPPET=UX_LAWS_SNIPPET,
            device_specs=device_specs_str
        )

        # 4. Enhance User Prompt with IA Context (if available)
        final_user_content = self.user_prompt
        if ia_context:
            iac_str = json.dumps(ia_context, indent=2)
            final_user_content = (
                f"{self.user_prompt}\n\n"
                f"<information_architecture_context>\n"
                f"You are part of a larger app. Here is the full Sitemap/IA for context. "
                f"Use this to ensure any navigation links (navigates_to) or hierarchy align with the global plan.\n"
                f"{iac_str}\n"
                f"</information_architecture_context>"
            )

        messages = [
            {"role": "system", "content": formatted_system_prompt},
            {"role": "user", "content": final_user_content}
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
            code=normalized_code,
            sub_prompt=self.user_prompt
        )

        return component