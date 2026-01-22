import os
from typing import List, Dict, Any

import google.genai as genai
from google.genai.types import SafetySetting, HarmCategory, GenerateContentConfig
from llm.providers.schemas import GEMINI_GENERATOR_SCHEMA, COMPONENT_JSON_SCHEMA_TEXT
from llm.providers.factory import LLMProvider
from exceptions import LLMAPIKeyMissingError, LLMProviderCompletionFailedException
from logs import logger


def _format_messages(messages: List[Dict[str, str]]) -> Dict[str, Any]:
    """Separates the system prompt and formats the chat history."""
    system_instruction = None
    contents = []
    for message in messages:
        if message["role"] == "system":
            # The new API prefers a single system instruction.
            system_instruction = message["content"]
        else:
            # The API expects the 'content' to be under a 'parts' key.
            contents = message["content"]
    return {"system_instruction": system_instruction, "contents": contents}

class GeminiProvider(LLMProvider):
    def __init__(self, model_name: str, config: Any):
        self.api_key = os.environ.get("GOOGLE_API_KEY")
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None
        self.model_name = model_name
        self.config = config

    def completion(self, messages: List[Dict[str, str]]) -> str:
        if not self.client:
            raise LLMAPIKeyMissingError("Google API key not configured")

        try:

            safety_settings: List[SafetySetting] = [
                {"category": HarmCategory.HARM_CATEGORY_HARASSMENT, "threshold": "BLOCK_NONE"},
                {"category": HarmCategory.HARM_CATEGORY_HATE_SPEECH, "threshold": "BLOCK_NONE"},
                {"category": HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, "threshold": "BLOCK_NONE"},
                {"category": HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, "threshold": "BLOCK_NONE"},
            ]

            formatted_messages = _format_messages(messages)

            generation_config = GenerateContentConfig(
                response_mime_type="application/json",
                system_instruction=formatted_messages["system_instruction"],
                safety_settings=safety_settings,
                response_schema=GEMINI_GENERATOR_SCHEMA
            )

            
            response = self.client.models.generate_content(
                model=f"models/{self.model_name}",
                contents=formatted_messages["contents"],
                config=generation_config
            )

            if response.prompt_feedback and response.prompt_feedback.block_reason:
                 raise LLMProviderCompletionFailedException(
                    f"Content blocked by safety filters: {response.prompt_feedback.block_reason.name}"
                )
            
            return response.text

        except Exception as e:
            logger.error(f"Gemini API request failed: {str(e)}")
            raise LLMProviderCompletionFailedException(f"Gemini API request failed: {str(e)}")

    def is_available(self) -> bool:
        return self.client
        
    def close(self):
        """Closes the underlying client session if applicable."""
        if self.client and hasattr(self.client, "close"):
            try:
                self.client.close()
            except Exception as e:
                logger.warning(f"Failed to close Gemini sync client: {e}")
    

class AsyncGeminiProvider(LLMProvider):
    def __init__(self, model_name: str, config: Any):
        self.api_key = os.environ.get("GOOGLE_API_KEY")
        self.model_name = model_name
        self.config = config
        
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
            self.async_client = self.client.aio
        else:
            self.client = None
            self.async_client = None


    async def completion(self, messages: List[Dict[str, str]]) -> str:
        if not self.async_client:
            raise LLMAPIKeyMissingError("Google API key not configured")

        try:

            safety_settings: List[SafetySetting] = [
                {"category": HarmCategory.HARM_CATEGORY_HARASSMENT, "threshold": "BLOCK_NONE"},
                {"category": HarmCategory.HARM_CATEGORY_HATE_SPEECH, "threshold": "BLOCK_NONE"},
                {"category": HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, "threshold": "BLOCK_NONE"},
                {"category": HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, "threshold": "BLOCK_NONE"},
            ]

            formatted_messages = _format_messages(messages)

            system_instruction = formatted_messages["system_instruction"]
            if system_instruction:
                schema_section = f"""
                    <json_schema>
                    Your output MUST conform to the following JSON schema. This schema defines the exact structure, property types, and valid values for the component tree. Pay special attention to:
                    - The "children" property uses "$ref": "#" which means it recursively references the root schema - children can contain the same structure as the parent
                    - Only "type" is required at the root level
                    - Use only the enum values specified for properties like type, align, justify, etc.

                    ```json
                    {COMPONENT_JSON_SCHEMA_TEXT}
                    ```
                    </json_schema>

                    """
                system_instruction = schema_section + system_instruction

            generation_config = GenerateContentConfig(
                response_mime_type="application/json",
                system_instruction=system_instruction,
                safety_settings=safety_settings
            )

            response = await self.async_client.models.generate_content(
                model=self.model_name,
                contents=formatted_messages["contents"],
                config=generation_config
            )

            if response.prompt_feedback and response.prompt_feedback.block_reason:
                 raise LLMProviderCompletionFailedException(
                    f"Content blocked by safety filters: {response.prompt_feedback.block_reason.name}"
                )
            
            return response.text

        except Exception as e:
            logger.error(f"Gemini API request failed: {str(e)}")
            raise LLMProviderCompletionFailedException(f"Gemini API request failed: {str(e)}")

    def is_available(self) -> bool:
        return self.async_client
        
    async def close(self):
        """Closes the underlying client session."""
        try:
            if self.async_client:
                # Attempt to find the underlying aiohttp session hidden in the client
                # Structure found via inspection: async_client._api_client._aiohttp_session
                if hasattr(self.async_client, "_api_client"):
                    api_client = self.async_client._api_client
                    if hasattr(api_client, "_aiohttp_session") and api_client._aiohttp_session:
                        await api_client._aiohttp_session.close()
                
                # Also try standard close if it exists (it returned False in inspection but good practice)
                if hasattr(self.async_client, "close"):
                    await self.async_client.close()

        except Exception as e:
            logger.warning(f"Error during AsyncGeminiProvider cleanup: {e}")

        # Sync client cleanup
        if self.client and hasattr(self.client, "close"):
            try:
                self.client.close()
            except: pass

        # Allow time for underlying aiohttp connector to close
        import asyncio
        await asyncio.sleep(0.250)