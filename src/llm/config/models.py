from dataclasses import dataclass
from enum import Enum


@dataclass
class TemperatureOptions:
    default: float
    creative: float


@dataclass 
class LLMModelConfig:
    name: str
    description: str
    max_tokens: int
    temperature_options: TemperatureOptions
    
MAX_TOKENS_OPENAI = 8192
class LLMAvailableModels(Enum):
    GPT_4 = LLMModelConfig(
        name="gpt-4",
        description="OpenAI GPT-4 model",
        max_tokens=MAX_TOKENS_OPENAI,
        temperature_options=TemperatureOptions(
            default=0.7,
            creative=1.0,
        )
    )

    GPT_5_MINI = LLMModelConfig(
        name="gpt-5-mini",
        description="OpenAI GPT-5-mini model",
        max_tokens=MAX_TOKENS_OPENAI,
        temperature_options=TemperatureOptions(
            default=1,
            creative=1.0,
        )
    )

    GPT_o3 = LLMModelConfig(
        name="o3",
        description="OpenAI o3 model",
        max_tokens=MAX_TOKENS_OPENAI,
        temperature_options=TemperatureOptions(
            default=1,
            creative=1.0,
        )
    )

    GPT_o4_MINI = LLMModelConfig(
        name="o4-mini",
        description="OpenAI 04-mini model",
        max_tokens=MAX_TOKENS_OPENAI,
        temperature_options=TemperatureOptions(
            default=1,
            creative=1.0,
        )
    )

    GEMINI_2_5_PRO =  LLMModelConfig(
        name="gemini-2.5-pro",
        description="Google Gemini 2.5 Pro model",
        max_tokens=10000,
        temperature_options=TemperatureOptions(
            default=0.7,
            creative=1.0
       )
    )

    GEMINI_3_PRO = LLMModelConfig(
        name="gemini-3-pro-preview",
        description="Google Gemini 3 Pro model",
        max_tokens=64000,
        temperature_options=TemperatureOptions(
            default=0.7,
            creative=1.0
        )
    )

    @classmethod
    def get_model_names(cls):
        return [model.value.name for model in cls]
