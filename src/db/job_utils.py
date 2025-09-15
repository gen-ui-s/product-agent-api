from typing import List, Dict, Any, Optional
from models.db_models import Job, Component
from job_config import JobStatus, ComponentStatus
from exceptions import JobNotFoundException, JobStatusUpdateFailedException, ComponentsNotFoundException, ComponentStatusUpdateFailedException

def insert_job_record(db: Dict, job_data: Dict[str, Any]) -> str:
    try:
        Job(**job_data)
        result = db["generation_jobs"].insert_one(job_data)
        
        return str(result.inserted_id)
    except Exception as e:
        raise Exception(f"Failed to create job record: {str(e)}")


def insert_component_records(db: Dict, components_data: List[Dict[str, Any]]) -> List[str]:
    try:        
        for data in components_data:
            Component(**data)
        
        result = db["generated_components"].insert_many(components_data)
        
        return [str(inserted_id) for inserted_id in result.inserted_ids]
    except Exception as e:
        raise Exception(f"Failed to create component records: {str(e)}")


def find_job_by_id(db: Dict, job_id: str) -> Optional[Dict[str, Any]]:
    try:
        job = db["generation_jobs"].find_one({"_id": job_id})
    except Exception as e:
        raise JobNotFoundException(f"Database query failed: {e}")
    return job


def find_job_components(db: Dict, job_id: str) -> List[Dict[str, Any]]:
    try:
        component_docs = list(db["generated_components"].find({"parent_job_id": job_id}))
    except Exception as e:
        raise ComponentsNotFoundException(f"Database query failed: {e}")

    return component_docs


def update_job_status(db: Dict, job_id: str, new_status: JobStatus) -> bool:
    try:
        result = db["generation_jobs"].update_one(
            {"_id": job_id},
            {"$set": {"status": new_status.value}}
        )
        return result.modified_count > 0
    except Exception as e:
        raise JobStatusUpdateFailedException(f"Failed to update job status: {str(e)}")


def update_component_status(db: Dict, component_id: str, new_status: ComponentStatus) -> bool:
    try:
        result = db["generated_components"].update_one(
            {"_id": component_id},
            {"$set": {"status": new_status.value}}
        )
        return result.modified_count > 0
    except Exception as e:
        raise ComponentStatusUpdateFailedException(f"Failed to update component status: {str(e)}")


def update_component_with_result(db: Dict, component_id: str, status: ComponentStatus, code: str = None, error_message: str = None, completed_at: str = None) -> bool:
    try:
        update_data = {"status": status.value}
        if code is not None:
            update_data["code"] = code
        if error_message is not None:
            update_data["error_message"] = error_message
        if completed_at is not None:
            update_data["completed_at"] = completed_at

        result = db["generated_components"].update_one(
            {"_id": component_id},
            {"$set": update_data}
        )
        return result.modified_count > 0
    except Exception as e:
        raise ComponentStatusUpdateFailedException(f"Failed to update component with result: {str(e)}")
