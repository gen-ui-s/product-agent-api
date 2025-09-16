from typing import List, Dict
from pydantic import BaseModel

import os

import google.generativeai as genai
from llm.providers.factory import LLMProvider
from google.api_core.exceptions import ResourceExhausted, ServiceUnavailable
from exceptions import LLMAPIKeyMissingError, LLMProviderCompletionFailedException
from logs import logger
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from pydantic import BaseModel
from typing import List

class Screen(BaseModel):
    screen_name: str
    sub_prompt: str

class ScreenGenerationResponse(BaseModel):
    screens: List[Screen]

class GeminiProvider(LLMProvider):
    def __init__(self, model_name: str, config):
        self.api_key = os.environ.get("GOOGLE_API_KEY")
        self.model_name = model_name
        self.config = config

        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel(self.model_name)
        else:
            self.client = None
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        retry=retry_if_exception_type((ResourceExhausted, ServiceUnavailable))
    )
    def completion(self, messages: List[Dict[str, str]]) -> str:
        if not self.client:
            raise LLMAPIKeyMissingError("Google API key not configured")
            
        try:
            generation_config = genai.GenerationConfig(
                temperature=self.config.temperature_options.default,
                max_output_tokens=self.config.max_tokens,
                response_mime_type="application/json",
                response_schema=ScreenGenerationResponse
            )

            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]

            full_prompt = ""
            for message in messages:
                if message["role"] == "system":
                    full_prompt += f"Instructions: {message['content']}\n\n"
                elif message["role"] == "user":
                    full_prompt += f"User: {message['content']}\n"

            basic_model = genai.GenerativeModel('gemini-2.5-pro')

            response = basic_model.generate_content(
                full_prompt,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            if not response.candidates:
                raise Exception("No response candidates returned by Gemini API")
                
            candidate = response.candidates[0]
            if not candidate.content or not candidate.content.parts:
                finish_reason = candidate.finish_reason
                if finish_reason == 2:  # SAFETY
                    raise Exception("Content blocked by safety filters - try using GPT-4 instead")
                elif finish_reason == 3:  # RECITATION  
                    raise Exception("Content blocked due to recitation - try rephrasing")
                else:
                    raise Exception(f"No content generated, reason: {finish_reason}")
            
            return response.text
            
        except (ResourceExhausted, ServiceUnavailable) as e:
            logger.warning(f"Gemini API transient error: {str(e)}. Retrying...")
            raise e
        except Exception as e:
            logger.error(f"Gemini API request failed: {str(e)}")
            raise LLMProviderCompletionFailedException(f"Gemini API request failed: {str(e)}")
    
    def is_available(self) -> bool:
        return self.client is not None

class AsyncGeminiProvider(LLMProvider):
    def __init__(self, model_name, config):
        self.api_key = os.environ.get("GOOGLE_API_KEY")
        self.model_name = model_name
        self.config = config

        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel(self.model_name)
        else:
            self.client = None
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        retry=retry_if_exception_type((ResourceExhausted, ServiceUnavailable))
    )
    async def completion(self, messages: List[Dict[str, str]], force_json: bool = False) -> str:
        if not self.client:
            raise LLMAPIKeyMissingError("Google API key not configured")

        try:
            if force_json:
                generation_config = genai.GenerationConfig(
                    temperature=self.config.temperature_options.default,
                    max_output_tokens=self.config.max_tokens,
                    response_mime_type="application/json",
                    response_schema=ScreenGenerationResponse
                )
            else:
                generation_config = genai.GenerationConfig(
                    temperature=self.config.temperature_options.default,
                    max_output_tokens=self.config.max_tokens
                )

            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]

            full_prompt = ""
            for message in messages:
                if message["role"] == "system":
                    full_prompt += f"Instructions: {message['content']}\n\n"
                elif message["role"] == "user":
                    full_prompt += f"User: {message['content']}\n"

            response = await self.client.generate_content_async(
                full_prompt,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            if not response.candidates:
                raise Exception("No response candidates returned by Gemini API")
                
            candidate = response.candidates[0]
            if not candidate.content or not candidate.content.parts:
                finish_reason = candidate.finish_reason
                if finish_reason == 2:  # SAFETY
                    raise Exception("Content blocked by safety filters - try using GPT-4 instead")
                elif finish_reason == 3:  # RECITATION  
                    raise Exception("Content blocked due to recitation - try rephrasing")
                else:
                    raise Exception(f"No content generated, reason: {finish_reason}")
            
            return response.text
            
        except (ResourceExhausted, ServiceUnavailable) as e:
            logger.warning(f"Gemini API transient error: {str(e)}. Retrying...")
            raise e
        except Exception as e:
            logger.error(f"Gemini API request failed: {str(e)}")
            raise LLMProviderCompletionFailedException(f"Gemini API request failed: {str(e)}")
    
    def is_available(self) -> bool:
        return self.client is not None

