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
    

class LLMAvailableModels(Enum):
    GPT_4 = LLMModelConfig(
        name="gpt-4",
        description="OpenAI GPT-4 model",
        max_tokens=5000,
        temperature_options=TemperatureOptions(
            default=0.7,
            creative=1.0,
        )
    )

    GPT_5 = LLMModelConfig(
        name="gpt-5",
        description="OpenAI GPT-5 model",
        max_tokens=5000,
        temperature_options=TemperatureOptions(
            default=0.7,
            creative=1.0,
        )
    )

    GPT_5_MINI = LLMModelConfig(
        name="gpt-5-mini",
        description="OpenAI GPT-5 model",
        max_tokens=5000,
        temperature_options=TemperatureOptions(
            default=0.7,
            creative=1.0,
        )
    )
    
    GEMINI_2_5_PRO =  LLMModelConfig(
        name="gemini-2.5-pro",
        description="Google Gemini 2" \
        ".5 Pro model",
        max_tokens=10000,
        temperature_options=TemperatureOptions(
            default=0.7,
            creative=1.0
       )
    )

    @classmethod
    def get_model_names(cls):
        return [model.value.name for model in cls]
