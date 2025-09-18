from enum import Enum


from llm.config.models import LLMAvailableModels
from llm.providers.base import LLMProvider
from llm.providers.openai import OpenAIProvider, AsyncOpenAIProvider
from llm.providers.google import GeminiProvider, AsyncGeminiProvider
from logs import logger


class ProviderType(str, Enum):
    SYNC = "sync"
    ASYNC = "async" 

class LLMFactory:
    """Factory to create appropriate LLM provider"""
    
    _providers = {
        LLMAvailableModels.GPT_4.value.name: {"class": OpenAIProvider, "config": LLMAvailableModels.GPT_4.value},
        LLMAvailableModels.GEMINI_2_5_PRO.value.name: {"class": GeminiProvider, "config": LLMAvailableModels.GEMINI_2_5_PRO.value}
    }

    _async_providers = {
        LLMAvailableModels.GPT_4.value.name: {"class": AsyncOpenAIProvider, "config": LLMAvailableModels.GPT_4.value},
        LLMAvailableModels.GEMINI_2_5_PRO.value.name: {"class": AsyncGeminiProvider, "config": LLMAvailableModels.GEMINI_2_5_PRO.value}
    }

    @classmethod
    def _create_provider_base(cls, model_name: str, provider_type: ProviderType) -> LLMProvider:
        providers_dict = cls._providers if provider_type == ProviderType.SYNC else cls._async_providers

        provider_data = providers_dict.get(model_name)
        if not provider_data:
            raise ValueError(f"Unsupported model: {model_name}")

        provider_class = provider_data["class"]
        logger.info(f"Instantiating provider: {provider_class}")

        provider = provider_class(
            model_name=model_name,
            config=provider_data["config"])
        if not provider.is_available():
            raise ValueError(f"Provider for {model_name} is not properly configured")

        return provider

    @classmethod
    def create_provider(cls, model_name: str) -> LLMProvider:
        return cls._create_provider_base(model_name, ProviderType.SYNC)

    @classmethod
    def create_async_provider(cls, model_name: str) -> LLMProvider:
        return cls._create_provider_base(model_name, ProviderType.ASYNC)