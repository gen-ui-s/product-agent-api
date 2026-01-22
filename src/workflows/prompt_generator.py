import json
from models.db_models import Job
from exceptions import PromptGenerationFailedException, DeviceSizeNotFoundException
from llm.providers.factory import LLMFactory
from workflows.prompts.prompt_gen import PROMPT_ENHANCER, INFORMATION_ARCHITECTURE, SCREEN_SUB_PROMPT_GENERATOR_AGENT
from workflows.prompts.general import JSON_RULES_SNIPPET, UX_LAWS_SNIPPET
from job_config import AvailableDeviceSizes
from logs import logger

class PromptGenerator:
    def __init__(self, job_data: Job):
        self.job_data: Job = job_data 
    
    def run(self):            
        try:
            logger.info("Starting Chained Planning Phase...")
            provider = LLMFactory.create_provider(self.job_data["model"])
            
            try:
                # 0. Setup Context
                user_prompt = self.job_data["user_prompt"]
                screen_count = self.job_data["screen_count"]
                generation_type = self.job_data["generation_type"]
                # Detect device size or default
                device = self.job_data.get("device")
                if not device or "name" not in device:
                    raise DeviceSizeNotFoundException("Device information is missing from job data.")
                
                device_name = device["name"]
                try:
                    device_enum = AvailableDeviceSizes.get_device_by_name(device_name)
                    # Store device info as dict
                    device_info = {
                        "name": device_enum.name,
                        "width": device_enum.width,
                        "height": device_enum.height,
                        "corner_radius": device_enum.corner_radius
                    }
                except ValueError:
                     raise DeviceSizeNotFoundException("Device size not found for device: " + device_name)
    
                # ------------------------------------------------------------------
                # STEP 1: PROMPT ENHANCER
                # ------------------------------------------------------------------
                logger.info("Step 1: Enhancing User Prompt...")
                enhancer_system = PROMPT_ENHANCER.format(
                    json_rules=JSON_RULES_SNIPPET,
                    ux_laws=UX_LAWS_SNIPPET,
                    device_info=json.dumps(device_info, indent=2)
                )
                
                msgs_1 = [
                    {"role": "system", "content": enhancer_system},
                    {"role": "user", "content": user_prompt}
                ]
                resp_1_str = provider.completion(messages=msgs_1)
                brief_json = json.loads(resp_1_str)
                logger.info("Prompt Enhanced successfully.")
    
                # ------------------------------------------------------------------
                # STEP 2: INFORMATION ARCHITECTURE
                # ------------------------------------------------------------------
                logger.info("Step 2: Designing Information Architecture...")
                ia_system = INFORMATION_ARCHITECTURE.format(
                    json_rules=JSON_RULES_SNIPPET,
                    ux_laws=UX_LAWS_SNIPPET,
                    device_info=json.dumps(device_info, indent=2)
                )
                # Pass the enhanced brief as input
                msgs_2 = [
                    {"role": "system", "content": ia_system},
                    {"role": "user", "content": json.dumps(brief_json, indent=2)}
                ]
                resp_2_str = provider.completion(messages=msgs_2)
                sitemap_json = json.loads(resp_2_str)
                logger.info(f"Sitemap generated with {len(sitemap_json.get('screens', []))} screens.")
    
                # ------------------------------------------------------------------
                # STEP 3: SUB-PROMPT GENERATOR
                # ------------------------------------------------------------------
                logger.info("Step 3: Generating Screen Sub-Prompts...")
                sub_gen_system = SCREEN_SUB_PROMPT_GENERATOR_AGENT.format(
                    json_rules=JSON_RULES_SNIPPET,
                    ux_laws=UX_LAWS_SNIPPET,
                    device_info=json.dumps(device_info, indent=2)
                )
                
                # Prepare input for sub-prompter
                sub_gen_input = {
                    **sitemap_json,  # merge sitemap details
                    "generation_type": generation_type,
                    "screen_count": screen_count
                }
    
                msgs_3 = [
                    {"role": "system", "content": sub_gen_system},
                    {"role": "user", "content": json.dumps(sub_gen_input, indent=2)}
                ]
                resp_3_str = provider.completion(messages=msgs_3)
                final_prompts_json = json.loads(resp_3_str)
                
                # Return both key artifacts: the detailed sub-prompts AND the sitemap context
                # (The workflow orchestrator will need to pass the sitemap to ComponentGenerator)
                return {
                    "optimized_prompt": str(brief_json),
                    "information_architecture": str(sitemap_json),
                    "sub_prompts": final_prompts_json,
                    "device_info": device_info
                }
            finally:
                if hasattr(provider, "close"):
                    provider.close()

        except Exception as e:
            logger.error(f"Planning Phase Failed: {str(e)}")
            raise PromptGenerationFailedException(f"Failed to execute planning chain: {str(e)}")
