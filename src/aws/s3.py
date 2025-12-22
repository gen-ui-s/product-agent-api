import os
import asyncio
import aioboto3
from typing import List, Dict
from logs import logger

async def upload_images_concurrently(image_data_map: Dict[str, List[bytes]]) -> Dict[str, List[str]]:
    """
    Uploads generated images to S3 concurrently.
    
    Args:
        image_data_map: Dictionary mapping component_id to a list of image bytes.
        
    Returns:
        Dictionary mapping component_id to a list of S3 URLs.
    """
    bucket_name = os.environ.get("AWS_S3_BUCKET")
    if not bucket_name:
        logger.error("AWS_S3_BUCKET environment variable not set")
        return {}

    session = aioboto3.Session()
    uploaded_urls_map = {}

    async with session.client("s3") as s3_client:
        tasks = []
        upload_metadata = [] # Stores (component_id, index, key)

        for component_id, images in image_data_map.items():
            uploaded_urls_map[component_id] = [None] * len(images)
            for idx, image_bytes in enumerate(images):
                # Generate unique key
                import uuid
                from datetime import datetime
                
                # Assume PNG for now as Imagen/Gemini usually outputs PNG/JPEG. 
                # Ideally we check magic bytes or response mime type.
                # Assuming PNG from user request context or defaults.
                extension = "png" 
                key = f"generated_images/{component_id}/{datetime.now().strftime('%Y%m%d')}/{uuid.uuid4()}.{extension}"
                
                upload_metadata.append((component_id, idx, key))
                
                tasks.append(
                    s3_client.put_object(
                        Bucket=bucket_name,
                        Key=key,
                        Body=image_bytes,
                        ContentType=f"image/{extension}"
                    )
                )
        
        if not tasks:
            return {}

        logger.info(f"Starting upload of {len(tasks)} images to S3 bucket {bucket_name}")
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for i, result in enumerate(results):
            component_id, idx, key = upload_metadata[i]
            if isinstance(result, Exception):
                logger.error(f"Failed to upload image {key} for component {component_id}: {result}")
                # Leave as None or set to empty string? None indicates failure.
            else:
                # Construct URL. 
                # If region is needed, we might need AWS_REGION. 
                # For standard buckets: https://bucket.s3.amazonaws.com/key
                # Or https://bucket.s3.region.amazonaws.com/key
                # We'll use the generic one or try to get region.
                region = os.environ.get("AWS_REGION", "us-east-1")
                url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{key}"
                uploaded_urls_map[component_id][idx] = url
                
    # Filter out None values from lists
    final_map = {}
    for cid, urls in uploaded_urls_map.items():
        valid_urls = [u for u in urls if u is not None]
        if valid_urls:
            final_map[cid] = valid_urls

    return final_map
