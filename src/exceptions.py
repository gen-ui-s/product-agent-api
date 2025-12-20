class DatabaseConnectionError(Exception):
    """Exception raised for errors in the database connection."""

class DatabaseQueryFailedException(Exception):
    """Raised if a query fails in the database"""

class LLMProviderCompletionFailedException(Exception):
    """LLMProviderException is raised for errors related to LLM providers."""

class LLMProviderInstantiationFailedException(Exception):
    """LLMCompletionException is raised for errors during LLM completion requests."""

class LLMProviderUnsupportedModelException(Exception):
    """LLMCompletionException is raised for errors during LLM completion requests."""

class LLMAPIKeyMissingError(Exception):
    """LLMAPIKeyMissingError is raised when the API key for the LLM provider is missing."""

class JobNotFoundException(Exception):
    """JobNotFoundException is raised when a job is not found in the database."""

class JobStatusUpdateFailedException(Exception):
    """JobStatusUpdateFailedException is raised when updating a job's status fails."""

class JobPromptUpdateFailedException(Exception):
 """JobPromprUpdateFailedException is raised when updating a job's status fails."""

class UserNotFoundException(Exception):
    """UserNotFoundException is raised when a user is not found in the database."""
    
class UserFailedUpdateException(Exception):
    """UserFailedUpdateException is raised when updating a user fails."""

class UserFailedInsertionException(Exception):
    """UserFailedInsertionException is raised when inserting a new user fails."""

class PromptGenerationFailedException(Exception):
    """ComponentGenerationException is raised for errors during component generation."""

class ComponentsNotFoundException(Exception):
    """ComponentsNotFoundException is raised when components related to a job are not found in the database."""

class ComponentGeneratedLengthMismatchException(Exception): 
    """ComponentGeneratedLengthMismatchException  is raised if componentes generated are not the same length as DB components"""

class ComponentStatusUpdateFailedException(Exception):
    """ComponentStatusUpdateFailedException is raised when updating a component's status fails."""

class ComponentGenerationFailedException(Exception):
    """ComponentGenerationException is raised for errors during component generation."""
    def __init__(self, message: str, invalid_code: str = None, sub_prompt: str = None):
        self.message = message
        self.invalid_code = invalid_code
        self.sub_prompt = sub_prompt
        super().__init__(self.message)
