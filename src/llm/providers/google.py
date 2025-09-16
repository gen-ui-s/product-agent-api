import os
from typing import List, Dict, Any

import google.genai as genai
from google.genai.types import GenerationConfig, SafetySettingDict, HarmCategory
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
            contents.append({'role': message['role'], 'parts': [message['content']]})
    return {"system_instruction": system_instruction, "contents": contents}

# --- Synchronous Provider for Structured JSON ---
class GeminiProvider(LLMProvider):
    def __init__(self, model_name: str, config: Any):
        self.api_key = os.environ.get("GOOGLE_API_KEY")
        self.model_name = model_name
        self.config = config

        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.client_configured = True
        else:
            self.client_configured = False

    def completion(self, messages: List[Dict[str, str]]) -> str:
        if not self.client_configured:
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
            generation_config = GenerationConfig(
                temperature=self.config.temperature_options.default,
                max_output_tokens=self.config.max_tokens,
                response_mime_type="application/json",
                response_schema=response_schema
            )

            safety_settings: List[SafetySettingDict] = [
                {"category": HarmCategory.HARM_CATEGORY_HARASSMENT, "threshold": "BLOCK_NONE"},
                {"category": HarmCategory.HARM_CATEGORY_HATE_SPEECH, "threshold": "BLOCK_NONE"},
                {"category": HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, "threshold": "BLOCK_NONE"},
                {"category": HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, "threshold": "BLOCK_NONE"},
            ]

            formatted_messages = _format_messages(messages)
            
            model = genai.GenerativeModel(
                self.model_name,
                system_instruction=formatted_messages["system_instruction"]
            )

            response = model.generate_content(
                contents=formatted_messages["contents"],
                generation_config=generation_config,
                safety_settings=safety_settings
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
        return self.client_configured

class AsyncGeminiProvider(LLMProvider):
    """
    Asynchronous Gemini provider for general-purpose text generation, with an
    option to force JSON output.
    """
    def __init__(self, model_name: str, config: Any):
        self.api_key = os.environ.get("GOOGLE_API_KEY")
        self.model_name = model_name
        self.config = config

        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.client_configured = True
        else:
            self.client_configured = False

    async def completion(self, messages: List[Dict[str, str]], force_json: bool = False) -> str:
        if not self.client_configured:
            raise LLMAPIKeyMissingError("Google API key not configured")

        try:
            gen_config_params = {
                "temperature": self.config.temperature_options.default,
                "max_output_tokens": self.config.max_tokens,
            }

            if force_json:
                gen_config_params["response_mime_type"] = "application/json"
                gen_config_params["response_schema"] = ScreenGenerationResponse.model_json_schema()

            generation_config = GenerationConfig(**gen_config_params)
            
            safety_settings: List[SafetySettingDict] = [
                {"category": HarmCategory.HARM_CATEGORY_HARASSMENT, "threshold": "BLOCK_NONE"},
                {"category": HarmCategory.HARM_CATEGORY_HATE_SPEECH, "threshold": "BLOCK_NONE"},
                {"category": HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, "threshold": "BLOCK_NONE"},
                {"category": HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, "threshold": "BLOCK_NONE"},
            ]
            
            formatted_messages = _format_messages(messages)
            
            model = genai.GenerativeModel(
                self.model_name,
                system_instruction=formatted_messages["system_instruction"]
            )

            response = await model.generate_content_async(
                contents=formatted_messages["contents"],
                generation_config=generation_config,
                safety_settings=safety_settings
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
        return self.client_configured