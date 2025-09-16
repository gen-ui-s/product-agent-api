import json
from models.db_models import Job
from exceptions import PromptGenerationFailedException
from llm.providers.factory import LLMFactory
from workflows.config.prompts import PROMPT_GENERATOR_SYSTEM_PROMPT
from logs import logger

class PromptGenerator:
    def __init__(self, job_data: Job):
        self.job_data: Job = job_data 
    
    def run(self):            
        try:
            logger.info("Generating screen prompts...")
            provider = LLMFactory.create_provider(self.job_data["model"])
            
            system_prompt = PROMPT_GENERATOR_SYSTEM_PROMPT.format(
                screen_count=self.job_data["screen_count"],
                generation_type=self.job_data["generation_type"],
                style_guide="Minimalist, pastel colors, serene, modern. Use SHADCN desing system principles."#TODO add design system information here.
                )
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": self.job_data["user_prompt"]}
            ]
            
            response = provider.completion(messages=messages)
        except Exception as e:
            raise PromptGenerationFailedException(f"Failed to create generation sub-prompts: {str(e)}")            
        
        return json.loads(response)   
