from typing import List, Dict
import os
from pydantic import BaseModel
from openai import OpenAI, AsyncOpenAI
from llm.providers.factory import LLMProvider
from exceptions import LLMAPIKeyMissingError, LLMProviderCompletionFailedException
from logs import logger

TIMEOUT = 120
class  OpenAIProvider(LLMProvider):
    def __init__(self, model_name: str, config):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None
        self.model_name = model_name
        self.config = config
        self.timeout = TIMEOUT

    def completion(self, messages: List[Dict[str, str]]) -> str:
        if not self.client:
            raise LLMAPIKeyMissingError("OpenAI API key not configured")
            
        response_schema = {
            "type": "json_schema",
            "json_schema": {
                "name": "screen_generation_response",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "screens": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "screen_name": {"type": "string", "description": "The name of the UI screen."},
                                    "sub_prompt": {"type": "string", "description": "A detailed prompt for generating this screen's content."}
                                },
                                "required": ["screen_name", "sub_prompt"],
                                "additionalProperties": False
                            }
                        }
                    },
                    "required": ["screens"],
                    "additionalProperties": False
                }
            }
        }
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.config.temperature_options.default,
                max_completion_tokens=self.config.max_tokens,
                timeout=self.timeout,
                response_format=response_schema
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API request failed: {str(e)}")
            raise LLMProviderCompletionFailedException(f"OpenAI API request failed: {str(e)}")
    
    def is_available(self) -> bool:
        return self.client is not None
    

class AsyncOpenAIProvider(LLMProvider):
    def __init__(self, model_name: str, config):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.client = AsyncOpenAI(api_key=self.api_key) if self.api_key else None
        self.model_name = model_name
        self.config = config
        self.timeout = TIMEOUT
        self.count = 0

    async def completion(self, messages: List[Dict[str, str]]) -> str:
        if not self.client:
            raise LLMAPIKeyMissingError("OpenAI API key not configured")
            
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.config.temperature_options.default,
                max_completion_tokens=self.config.max_tokens,
                timeout=self.timeout
            )
            self.count += 1
            logger.info(f"AsyncOpenAI {self.count} response: {response}")
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API request failed: {str(e)}")
            raise LLMProviderCompletionFailedException(f"OpenAI API request failed: {str(e)}")
    
    def is_available(self) -> bool:
        return self.client is not None