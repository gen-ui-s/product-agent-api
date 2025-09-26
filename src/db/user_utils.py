from typing import Dict
from exceptions import (
    UserNotFoundException,
    UserFailedUpdateException,
    UserFailedInsertionException
)


def insert_user(db: Dict, user_data: Dict) -> str:
    try:
        result = db["users"].insert_one(user_data)
    except Exception as e:
        raise UserFailedInsertionException(f"Failed to insert user: {str(e)}")
    
    return str(result.inserted_id)


def get_user_by_auth0_sub(db: Dict, auth0_sub: str) -> Dict:
    try:
        user = db["users"].find_one({"auth0_sub": auth0_sub})
    except Exception as e:
        raise UserNotFoundException(f"Database query failed: {e}")
    
    return user


def update_user(db: Dict, update_filter: Dict, update_data: Dict) -> None:
    try:
        db["users"].update_one(
            update_filter,
            {"$set": update_data}
        )
    except Exception as e:
        raise UserFailedUpdateException(f"Failed to update user: {e}")