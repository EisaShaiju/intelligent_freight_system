from pydantic import BaseModel, Field

class OrchestrationRequest(BaseModel):
    """Payload for triggering the anomaly resolution workflow."""
    package_id: str = Field(..., description="The unique identifier for the package.")
    current_location: str = Field(..., description="Where the package is currently scanned.")
    anomaly_type: str = Field(..., description="Type of issue (e.g., missed_connection, damaged).")

class OrchestrationResponse(BaseModel):
    """Standard response after successfully triggering a workflow."""
    status: str
    message: str
    package_id: str