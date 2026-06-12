from fastapi import APIRouter, HTTPException
from api.schemas import OrchestrationRequest, OrchestrationResponse

# Import the compiled LangGraph application with memory attached
from agents.supervisor import orchestration_graph 

router = APIRouter(
    prefix="/api/v1/orchestrator",
    tags=["Orchestration"]
)

@router.post("/trigger")
def trigger_workflow(request: OrchestrationRequest): # <-- FIX 1: Removed 'async'
    """
    Triggers the LangGraph multi-agent workflow to resolve a logistics anomaly,
    saving its conversational state securely under the package_id thread.
    """
    initial_state = {
        "package_id": request.package_id,
        "current_location": request.current_location,
        "anomaly_type": request.anomaly_type,
        "resolution_status": "pending",
        "messages": [("user", f"Anomaly detected: {request.anomaly_type} for package {request.package_id} at {request.current_location}. Please resolve.")]
    }
    
    try:
        # Define the thread configuration
        config = {"configurable": {"thread_id": request.package_id}}
        
        # --- FIX 2: Changed ainvoke to invoke, and removed await ---
        result = orchestration_graph.invoke(initial_state, config=config)
        
        final_state_messages = result.get("messages", [])
        final_agent_decision = final_state_messages[-1].content if final_state_messages else "No solution generated."
            
        return {
            "status": "success",
            "package_id": request.package_id,
            "resolution_status": result.get("resolution_status", "unknown"),
            "final_action_taken": final_agent_decision
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Orchestration failed: {str(e)}")


@router.get("/status/{package_id}")
def get_status(package_id: str): # <-- FIX 3: Removed 'async'
    """
    Retrieves the exact historical logs and current state of a specific package
    by pulling its snapshot from the SQLite checkpointer.
    """
    try:
        # Point to the exact same thread configuration
        config = {"configurable": {"thread_id": package_id}}
        
        # Read the state snapshot straight out of the database (this is a sync call)
        snapshot = orchestration_graph.get_state(config)
        
        # If the thread ID doesn't exist in the database tables yet
        if not snapshot.values:
            raise HTTPException(status_code=404, detail=f"No active resolution history found for package {package_id}")
            
        state_data = snapshot.values
        messages = state_data.get("messages", [])
        
        return {
            "package_id": package_id,
            "current_anomaly": state_data.get("anomaly_type"),
            "resolution_status": state_data.get("resolution_status"),
            "agent_checkpoint_history_count": len(messages),
            "latest_agent_update": messages[-1].content if messages else "No logs recorded."
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch status: {str(e)}")