import os
from typing import List, Dict, Any

import google.genai as genai
from google.genai.types import SafetySetting, HarmCategory, GenerateContentConfig, HttpOptions
from google.api_core import exceptions as google_exceptions
from pydantic import BaseModel

from llm.providers.factory import LLMProvider
from exceptions import LLMAPIKeyMissingError, LLMProviderCompletionFailedException
from logs import logger

class Screen(BaseModel):
    screen_name: str
    sub_prompt: str

class ScreenGenerationResponse(BaseModel):
    screens: List[Screen]

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
        self.client = genai.Client(api_key=self.api_key,http_options=HttpOptions(api_version='v1')) if self.api_key else None
        self.model_name = model_name
        self.config = config


    def completion(self, messages: List[Dict[str, str]]) -> str:
        if not self.client:
            raise LLMAPIKeyMissingError("Google API key not configured")

        try:
            response_schema = {
                "type": "object",
                "properties": {
                    "screens": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "screen_name": {"type": "string"},
                                "sub_prompt": {"type": "string"}
                            },
                            "required": ["screen_name", "sub_prompt"]
                        }
                    }
                },
                "required": ["screens"]
            }

            safety_settings: List[SafetySetting] = [
                {"category": HarmCategory.HARM_CATEGORY_HARASSMENT, "threshold": "BLOCK_NONE"},
                {"category": HarmCategory.HARM_CATEGORY_HATE_SPEECH, "threshold": "BLOCK_NONE"},
                {"category": HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, "threshold": "BLOCK_NONE"},
                {"category": HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, "threshold": "BLOCK_NONE"},
            ]

            formatted_messages = _format_messages(messages)

            logger.info(formatted_messages["contents"])

            generation_config = GenerateContentConfig(
                temperature=self.config.temperature_options.default,
                max_output_tokens=self.config.max_tokens,
                # response_mime_type="application/json",
                # system_instruction=formatted_messages["system_instruction"],
                # safety_settings=safety_settings,
                # response_schema=response_schema
            )

            for model in self.client.models.list():
                logger.info("MODELS")
                logger.info(model)
            
            response = self.client.models.generate_content(
                model="models/gemini-2.5-pro",
                contents=formatted_messages["contents"],
                config=generation_config
            )

            logger.info("RESPONSE")
            logger.info(response)

            if response.prompt_feedback.block_reason:
                raise LLMProviderCompletionFailedException(
                    f"Content blocked by safety filters: {response.prompt_feedback.block_reason.name}"
                )
            
            return response.text

        except (google_exceptions.ResourceExhausted, google_exceptions.ServiceUnavailable) as e:
            logger.error(f"Gemini API failed after retries: {str(e)}")
            raise LLMProviderCompletionFailedException(f"Gemini API resource error after retries: {str(e)}")
        except Exception as e:
            logger.error(f"Gemini API request failed: {str(e)}")
            raise LLMProviderCompletionFailedException(f"Gemini API request failed: {str(e)}")

    def is_available(self) -> bool:
        return self.client
    

class AsyncGeminiProvider(LLMProvider):
    def __init__(self, model_name: str, config: Any):
        self.api_key = os.environ.get("GOOGLE_API_KEY")
        self.client = genai.Client(api_key=self.api_key,http_options=HttpOptions(api_version='v1alpha')) if self.api_key else None
        self.model_name = model_name
        self.config = config


    def completion(self, messages: List[Dict[str, str]]) -> str:
        if not self.client:
            raise LLMAPIKeyMissingError("Google API key not configured")

        try:
            response_schema = {
                "type": "object",
                "properties": {
                    "screens": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "screen_name": {"type": "string"},
                                "sub_prompt": {"type": "string"}
                            },
                            "required": ["screen_name", "sub_prompt"]
                        }
                    }
                },
                "required": ["screens"]
            }

            safety_settings: List[SafetySetting] = [
                {"category": HarmCategory.HARM_CATEGORY_HARASSMENT, "threshold": "BLOCK_NONE"},
                {"category": HarmCategory.HARM_CATEGORY_HATE_SPEECH, "threshold": "BLOCK_NONE"},
                {"category": HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, "threshold": "BLOCK_NONE"},
                {"category": HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, "threshold": "BLOCK_NONE"},
            ]

            formatted_messages = _format_messages(messages)

            logger.info(formatted_messages["contents"])

            generation_config = GenerateContentConfig(
                temperature=self.config.temperature_options.default,
                max_output_tokens=self.config.max_tokens,
                # response_mime_type="application/json",
                # system_instruction=formatted_messages["system_instruction"],
                # safety_settings=safety_settings,
                # response_schema=response_schema
            )

            
            response = self.client.models.generate_content_async(
                model=self.model_name,
                contents=formatted_messages["contents"],
                config=generation_config
            )


            if response.prompt_feedback.block_reason:
                raise LLMProviderCompletionFailedException(
                    f"Content blocked by safety filters: {response.prompt_feedback.block_reason.name}"
                )
            
            return response.text

        except (google_exceptions.ResourceExhausted, google_exceptions.ServiceUnavailable) as e:
            logger.error(f"Gemini API failed after retries: {str(e)}")
            raise LLMProviderCompletionFailedException(f"Gemini API resource error after retries: {str(e)}")
        except Exception as e:
            logger.error(f"Gemini API request failed: {str(e)}")
            raise LLMProviderCompletionFailedException(f"Gemini API request failed: {str(e)}")

    def is_available(self) -> bool:
        return self.client