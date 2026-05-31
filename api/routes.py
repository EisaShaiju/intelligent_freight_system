from fastapi import APIRouter, HTTPException
from api.schemas import OrchestrationRequest, OrchestrationResponse

# Import the compiled LangGraph application we built earlier
from agents.supervisor import orchestrator_app

router = APIRouter(
    prefix="/api/v1/orchestrator",
    tags=["Orchestration"]
)

@router.post("/trigger", response_model=OrchestrationResponse)
async def trigger_workflow(request: OrchestrationRequest):
    """
    Triggers the LangGraph multi-agent workflow to resolve a logistics anomaly.
    """
    # 1. Translate the incoming API request into the format our LangGraph state expects
    initial_state = {
        "package_id": request.package_id,
        "current_location": request.current_location,
        "anomaly_type": request.anomaly_type,
        "resolution_status": "pending",
        # We give the supervisor an initial prompt to start the conversation
        "messages": [("user", f"Anomaly detected: {request.anomaly_type} for package {request.package_id} at {request.current_location}. Please resolve.")]
    }
    
    try:
        # 2. Invoke the graph synchronously for this demo 
        # (In a massive production system, you'd use background tasks or Celery here)
        result = await orchestrator_app.ainvoke(initial_state)
        
        return OrchestrationResponse(
            status="success",
            message="Workflow completed and resolution orchestrated.",
            package_id=request.package_id
        )
    except Exception as e:
        # If the LLM fails or tools crash, return a clean 500 error
        raise HTTPException(status_code=500, detail=f"Orchestration failed: {str(e)}")

@router.get("/status/{package_id}")
async def get_status(package_id: str):
    """
    Retrieves the status of a specific package's resolution.
    Note: Requires a database (like Postgres/RDS) to be fully implemented.
    """
    # For now, this is a placeholder to show where your DB query would go
    return {
        "package_id": package_id, 
        "status": "In a full deployment, this would query Postgres for the agent's historical logs."
    }