from typing import List, Dict
import os
from openai import OpenAI, AsyncOpenAI
from llm.providers.factory import LLMProvider
from exceptions import LLMAPIKeyMissingError, LLMProviderCompletionFailedException
from logs import logger

class  OpenAIProvider(LLMProvider):
    def __init__(self, model_name: str, config):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None
        self.model_name = model_name
        self.config = config
        self.timeout = 30
        
    def completion(self, messages: List[Dict[str, str]]) -> str:
        if not self.client:
            raise LLMAPIKeyMissingError("OpenAI API key not configured")
            
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.config.temperature_options.default,
                max_tokens=self.config.max_tokens,
                timeout=self.timeout
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
        self.timeout = 30
        
    async def completion(self, messages: List[Dict[str, str]]) -> str:
        if not self.client:
            raise LLMAPIKeyMissingError("OpenAI API key not configured")
            
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.config.temperature_options.default,
                max_tokens=self.config.max_tokens,
                timeout=self.timeout
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API request failed: {str(e)}")
            raise LLMProviderCompletionFailedException(f"OpenAI API request failed: {str(e)}")
    
    def is_available(self) -> bool:
        return self.client is not None