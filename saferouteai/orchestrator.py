"""Multi-Agent Orchestrator for SafeRouteAI - coordinates all agents."""
from typing import Dict, Any, Optional, List
import asyncio
from datetime import datetime
import json

from saferouteai.agents.route_analysis_agent import RouteAnalysisAgent
from saferouteai.agents.safety_data_agent import SafetyDataAgent
from saferouteai.agents.risk_scoring_agent import RiskScoringAgent
from saferouteai.agents.route_optimization_agent import RouteOptimizationAgent
from saferouteai.agents.alert_agent import AlertAgent
from saferouteai.memory.session_manager import SessionManager
from saferouteai.observability.logger import setup_logger, get_logger
from saferouteai.observability.tracer import Tracer


class SafeRouteOrchestrator:
    """Orchestrates multiple agents to provide complete route safety analysis."""
    
    def __init__(self, session_id: Optional[str] = None, enable_memory: bool = True):
        """
        Initialize orchestrator with all agents.
        
        Args:
            session_id: Optional session ID for memory management
            enable_memory: Whether to enable session memory
        """
        self.logger = setup_logger("SafeRouteOrchestrator")
        self.tracer = Tracer()
        
        # Initialize agents
        self.route_agent = RouteAnalysisAgent()
        self.safety_agent = SafetyDataAgent()
        self.risk_agent = RiskScoringAgent()
        self.optimization_agent = RouteOptimizationAgent()
        self.alert_agent = AlertAgent()
        
        # Initialize session manager
        self.session_manager = SessionManager() if enable_memory else None
        self.session_id = session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if self.session_manager:
            self.session_manager.create_session(self.session_id)
            self.logger.info(f"Created session: {self.session_id}")
    
    async def analyze_route_safety(
        self,
        start: str,
        destination: str,
        route_type: str = "driving-car",
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Complete route safety analysis using multi-agent system.
        
        Args:
            start: Start location (address or "lat,lon")
            destination: Destination location (address or "lat,lon")
            route_type: Type of route (driving-car, foot-walking, cycling-regular)
            user_preferences: Optional user preferences (risk tolerance, etc.)
        
        Returns:
            Complete safety analysis with all agent outputs
        """
        with self.tracer.trace("analyze_route_safety"):
            self.logger.info(f"Starting route analysis: {start} -> {destination}")
            
            try:
                # Step 1: Route Analysis Agent (Sequential)
                with self.tracer.trace("route_analysis"):
                    self.logger.info("Step 1: Analyzing route...")
                    route_result = await self.route_agent.analyze_route(
                        start, destination, route_type
                    )
                    
                    route_data = route_result.get("route_data", {})
                    if not route_data.get("success"):
                        # Check if fallback data is available
                        if route_data.get("fallback"):
                            self.logger.warning(f"Using fallback route data: {route_data.get('error', 'Unknown error')}")
                            # Use fallback data
                            route_result["route_data"] = {
                                **route_data.get("fallback", {}),
                                "success": True,
                                "is_fallback": True,
                                "error": route_data.get("error", "")
                            }
                        else:
                            return {
                                "success": False,
                                "error": "Failed to analyze route",
                                "details": route_result
                            }
                
                # Step 2: Safety Data Agent (Parallel data gathering)
                with self.tracer.trace("safety_data_gathering"):
                    self.logger.info("Step 2: Gathering safety data...")
                    route_coords = route_result["route_data"].get("coordinates", [])
                    
                    if not route_coords:
                        return {
                            "success": False,
                            "error": "No route coordinates available"
                        }
                    
                    safety_result = await self.safety_agent.gather_safety_data(route_coords)
                
                # Step 3: Risk Scoring Agent (Sequential)
                with self.tracer.trace("risk_scoring"):
                    self.logger.info("Step 3: Calculating risk score...")
                    risk_result = await self.risk_agent.score_route_risk(safety_result)
                
                # Step 4: Route Optimization Agent (Conditional - only if risk is high)
                optimization_result = None
                if risk_result.get("risk_score", 0) >= 4:  # Moderate or high risk
                    with self.tracer.trace("route_optimization"):
                        self.logger.info("Step 4: Optimizing route...")
                        optimization_result = await self.optimization_agent.optimize_route(
                            route_result,
                            risk_result,
                            safety_result
                        )
                
                # Step 5: Alert Agent (Sequential - final output)
                with self.tracer.trace("alert_generation"):
                    self.logger.info("Step 5: Generating safety alert...")
                    alert_result = await self.alert_agent.generate_alert(
                        risk_result,
                        route_result,
                        optimization_result
                    )
                
                # Compile complete result
                result = {
                    "success": True,
                    "session_id": self.session_id,
                    "timestamp": datetime.now().isoformat(),
                    "route_analysis": route_result,
                    "safety_data": safety_result,
                    "risk_assessment": risk_result,
                    "route_optimization": optimization_result,
                    "safety_alert": alert_result,
                    "summary": {
                        "start": start,
                        "destination": destination,
                        "route_type": route_type,
                        "distance_km": route_result["route_data"].get("distance_km", 0),
                        "duration_minutes": route_result["route_data"].get("duration_minutes", 0),
                        "risk_score": risk_result.get("risk_score", 0),
                        "risk_level": risk_result.get("risk_level", "Unknown"),
                        "optimization_recommended": optimization_result is not None and optimization_result.get("should_use_alternative", False)
                    }
                }
                
                # Store in memory if enabled
                if self.session_manager:
                    self.session_manager.store_route_analysis(self.session_id, result)
                    self.logger.info(f"Stored analysis in session: {self.session_id}")
                
                self.logger.info(f"Route analysis complete. Risk score: {result['summary']['risk_score']}")
                return result
                
            except Exception as e:
                self.logger.error(f"Error in route analysis: {str(e)}", exc_info=True)
                return {
                    "success": False,
                    "error": str(e),
                    "session_id": self.session_id
                }
    
    async def batch_analyze_routes(
        self,
        routes: List[Dict[str, str]],
        route_type: str = "driving-car"
    ) -> List[Dict[str, Any]]:
        """
        Analyze multiple routes in parallel (Parallel agents pattern).
        
        Args:
            routes: List of route dicts with 'start' and 'destination' keys
            route_type: Type of route
        
        Returns:
            List of analysis results
        """
        with self.tracer.trace("batch_analyze_routes"):
            self.logger.info(f"Batch analyzing {len(routes)} routes...")
            
            tasks = [
                self.analyze_route_safety(
                    route["start"],
                    route["destination"],
                    route_type
                )
                for route in routes
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    processed_results.append({
                        "success": False,
                        "error": str(result),
                        "route": routes[i]
                    })
                else:
                    processed_results.append(result)
            
            self.logger.info(f"Batch analysis complete: {len(processed_results)} results")
            return processed_results
    
    def get_session_history(self) -> List[Dict[str, Any]]:
        """Get route analysis history for current session."""
        if not self.session_manager:
            return []
        
        return self.session_manager.get_session_history(self.session_id)
    
    def get_user_preferences(self) -> Dict[str, Any]:
        """Get stored user preferences from memory."""
        if not self.session_manager:
            return {}
        
        return self.session_manager.get_user_preferences(self.session_id)
    
    def update_user_preferences(self, preferences: Dict[str, Any]):
        """Update user preferences in memory."""
        if self.session_manager:
            self.session_manager.update_user_preferences(self.session_id, preferences)
            self.logger.info(f"Updated user preferences for session: {self.session_id}")

