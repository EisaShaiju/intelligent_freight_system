from fastapi import APIRouter, HTTPException
from api.schemas import OrchestrationRequest, OrchestrationResponse

# Import the compiled LangGraph application we built earlier
# (Note: Ensure this matches the exact variable name exported from supervisor.py)
from agents.supervisor import orchestration_graph 

router = APIRouter(
    prefix="/api/v1/orchestrator",
    tags=["Orchestration"]
)

@router.post("/trigger")
async def trigger_workflow(request: OrchestrationRequest):
    """
    Triggers the LangGraph multi-agent workflow to resolve a logistics anomaly,
    and returns the exact execution plan drafted by the agents.
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
        # 2. Invoke the graph asynchronously 
        result = await orchestration_graph.ainvoke(initial_state)
        
        # 3. Extract the final message added by the last agent in the loop
        final_state_messages = result.get("messages", [])
        
        if final_state_messages:
            # Grab the text content of the very last LLM interaction
            final_agent_decision = final_state_messages[-1].content
        else:
            final_agent_decision = "No solution generated."
            
        # 4. Return the rich data back to the client
        return {
            "status": "success",
            "package_id": request.package_id,
            "resolution_status": result.get("resolution_status", "unknown"),
            "final_action_taken": final_agent_decision
        }
        
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