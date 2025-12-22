import os
import asyncio
import base64
from typing import List, Dict, Tuple
from google import genai
from google.genai import types
from logs import logger

# Models
# Fallback to standard Imagen 3 model as fast variant was# Models
IMAGEN_3_FAST = "models/imagen-4.0-fast-generate-001" 
GEMINI_2_5_FLASH = "gemini-2.5-flash-image"

async def _generate_single_image_set(client, model_name: str, prompt: str, count: int = 1) -> List[bytes]:
    """Generates images for a single prompt."""
    try:
        # Gemini 2.5 Flash Image uses generate_images or generate_content
        # Based on documentation, for image generation models it often uses generate_images
        # but configured differently.
        # Let's assume the standard client.models.generate_images works for it if it's in the list.
        # If not, we might need a fallback to generate_content, but let's try this standard path.

        response = await client.models.generate_images(
            model=model_name,
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=count,
            )
        )
        return [img.image.image_bytes for img in response.generated_images]

    except Exception as e:
        logger.error(f"Image generation failed for prompt '{prompt[:30]}...' with model {model_name}: {e}")
        return []

async def generate_images_concurrently(component_prompts: Dict[str, List[str]]) -> Dict[str, List[bytes]]:
    """
    Generates images concurrently for multiple components.
    
    Args:
        component_prompts: Dictionary mapping component_id to a list of prompt strings.
                           (e.g., {"comp1": ["avatar description"], "comp2": ["header bg"]})
    
    Returns:
        Dictionary mapping component_id to a list of generated image bytes.
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        logger.error("GOOGLE_API_KEY not set")
        return {}

    raw_client = genai.Client(api_key=api_key)
    client = raw_client.aio
    
    try:
        # Try primary model first, fallback logic could be complex concurrently.
        # For now, we fix to IMAGEN_3_FAST as per plan.
        model_name = IMAGEN_3_FAST
        tasks = []
        metadata = [] # (component_id, prompt_index)

        for component_id, prompts in component_prompts.items():
            for i, prompt in enumerate(prompts):
                metadata.append(component_id)
                # We generate 1 image per prompt for now. 
                tasks.append(_generate_single_image_set(client, model_name, prompt, count=1))

        logger.info(f"Starting concurrent image generation for {len(tasks)} prompts using {model_name}")
        results = await asyncio.gather(*tasks, return_exceptions=True)
    finally:
        try:
            # Deep cleanup to find the underlying aiohttp session
            if hasattr(client, "_api_client"):
                api_client = client._api_client
                if hasattr(api_client, "_aiohttp_session") and api_client._aiohttp_session:
                    await api_client._aiohttp_session.close()

            if hasattr(client, "close"):
                await client.close()
        except Exception as e:
            logger.warning(f"Error closing image gen client: {e}")
        
        if hasattr(raw_client, "close"):
            try:
                raw_client.close()
            except:
                pass

        # Allow time for underlying aiohttp connector to close
        await asyncio.sleep(0.250)
        # Hack/Workaround for aiohttp session inside genai client if plain close doesn't work well
        # or if it is inside .aio
    
    # ... (process results)
    
    final_images: Dict[str, List[bytes]] = {}

    for i, result in enumerate(results):
        component_id = metadata[i]
        
        if component_id not in final_images:
            final_images[component_id] = []
            
        if isinstance(result, list) and result:
            # Result is a list of bytes (we requested 1, so list of 1)
            final_images[component_id].extend(result)
        else:
             logger.warning(f"No images generated for component {component_id} (index {i})")

    return final_images
