"""
SafeRouteAI REST API Server
Deploy this to make your agent available online via HTTP API.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import asyncio
from saferouteai import SafeRouteOrchestrator
from saferouteai.observability.logger import setup_logger

# Setup
app = FastAPI(
    title="SafeRouteAI API",
    description="Real-Time Route Safety Advisor - Multi-Agent System",
    version="1.0.0"
)

# Enable CORS for web apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = setup_logger("SafeRouteAPI")


# Request/Response Models
class RouteRequest(BaseModel):
    start: str
    destination: str
    route_type: str = "driving-car"
    session_id: Optional[str] = None


class BatchRouteRequest(BaseModel):
    routes: list
    route_type: str = "driving-car"
    session_id: Optional[str] = None


@app.get("/")
def root():
    """API root endpoint."""
    return {
        "service": "SafeRouteAI API",
        "version": "1.0.0",
        "endpoints": {
            "analyze": "/api/analyze-route",
            "batch": "/api/batch-analyze",
            "health": "/api/health"
        }
    }


@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "SafeRouteAI"}


@app.post("/api/analyze-route")
async def analyze_route(request: RouteRequest):
    """
    Analyze a single route for safety.
    
    Request body:
    - start: Start location as "lat,lon"
    - destination: Destination as "lat,lon"
    - route_type: "driving-car", "foot-walking", or "cycling-regular"
    - session_id: Optional session ID for memory
    """
    try:
        logger.info(f"Analyzing route: {request.start} -> {request.destination}")
        
        orchestrator = SafeRouteOrchestrator(
            session_id=request.session_id or "api_session"
        )
        
        result = await orchestrator.analyze_route_safety(
            start=request.start,
            destination=request.destination,
            route_type=request.route_type
        )
        
        if not result.get("success", False):
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Route analysis failed")
            )
        
        return {
            "success": True,
            "risk_score": result['summary']['risk_score'],
            "risk_level": result['summary']['risk_level'],
            "distance_km": result['summary'].get('distance_km', 0),
            "duration_minutes": result['summary'].get('duration_minutes', 0),
            "alert": result['safety_alert']['alert']['formatted_alert'],
            "risk_breakdown": result['risk_assessment'].get('risk_breakdown', {}),
            "recommendation": result['risk_assessment'].get('recommendation', ''),
            "optimization_available": result['summary'].get('optimization_recommended', False)
        }
    except Exception as e:
        logger.error(f"Error analyzing route: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/batch-analyze")
async def batch_analyze(request: BatchRouteRequest):
    """
    Analyze multiple routes in parallel.
    
    Request body:
    - routes: List of {"start": "lat,lon", "destination": "lat,lon"}
    - route_type: Route type for all routes
    - session_id: Optional session ID
    """
    try:
        logger.info(f"Batch analyzing {len(request.routes)} routes")
        
        orchestrator = SafeRouteOrchestrator(
            session_id=request.session_id or "api_batch_session"
        )
        
        results = await orchestrator.batch_analyze_routes(
            routes=request.routes,
            route_type=request.route_type
        )
        
        # Format results
        formatted_results = []
        for result in results:
            if result.get("success", False):
                formatted_results.append({
                    "success": True,
                    "risk_score": result['summary']['risk_score'],
                    "risk_level": result['summary']['risk_level'],
                    "start": result['summary']['start'],
                    "destination": result['summary']['destination']
                })
            else:
                formatted_results.append({
                    "success": False,
                    "error": result.get("error", "Unknown error")
                })
        
        return {
            "success": True,
            "total_routes": len(results),
            "results": formatted_results
        }
    except Exception as e:
        logger.error(f"Error in batch analysis: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/session/{session_id}/history")
def get_session_history(session_id: str):
    """Get route analysis history for a session."""
    try:
        orchestrator = SafeRouteOrchestrator(session_id=session_id)
        history = orchestrator.get_session_history()
        return {
            "success": True,
            "session_id": session_id,
            "history": history
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

