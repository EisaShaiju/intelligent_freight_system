from fastapi import FastAPI
from api.routes import router

app = FastAPI(
    title="IBS Logistics Orchestrator API",
    description="RESTful gateway for the multi-agent freight resolution platform.",
    version="1.0.0"
)

# Attach the routes we defined in routes.py
app.include_router(router)

@app.get("/")
async def health_check():
    """Simple endpoint to verify the API is up and running."""
    return {
        "status": "healthy", 
        "service": "IBS Logistics Orchestrator",
        "docs_url": "/docs"
    }