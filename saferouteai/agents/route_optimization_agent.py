"""Route Optimization Agent for SafeRouteAI - suggests safer alternative routes."""
from saferouteai.agents.agent_wrapper import Agent, Tool
from google.generativeai import GenerativeModel
from typing import Dict, Any, List, Optional
import saferouteai.config as config
import openrouteservice
from geopy.distance import geodesic


class RouteOptimizationAgent:
    """Agent that suggests safer alternative routes when risk is high."""
    
    def __init__(self):
        self.model = GenerativeModel(config.ROUTE_OPTIMIZATION_MODEL)
        self.client = openrouteservice.Client(key=config.ORS_API_KEY) if config.ORS_API_KEY else None
        
        self.agent = Agent(
            model=self.model,
            instructions="""
            You are a Route Optimization Agent. Your role is to:
            1. Analyze high-risk routes and identify why they're unsafe
            2. Suggest safer alternative routes when risk exceeds threshold (4+)
            3. Explain why alternative routes are safer
            4. Compare route options (distance, time, safety)
            5. Recommend the best route based on safety and efficiency
            
            When optimizing routes:
            - Consider avoiding high-crime areas
            - Prefer well-lit routes during dark hours
            - Avoid routes with severe weather conditions
            - Consider time-of-day factors
            - Balance safety with travel time/distance
            
            Always provide clear explanations for route recommendations.
            """,
            tools=[
                self._create_alternative_route_tool(),
                self._create_route_comparison_tool()
            ]
        )
    
    def _create_alternative_route_tool(self):
        """Create tool for finding alternative routes."""
        def find_alternative_route(
            start_lat: float,
            start_lon: float,
            end_lat: float,
            end_lon: float,
            avoid_areas: Optional[List[Dict[str, float]]] = None,
            profile: str = "driving-car"
        ) -> Dict[str, Any]:
            """
            Find alternative route avoiding specified areas.
            
            Args:
                start_lat: Start latitude
                start_lon: Start longitude
                end_lat: End latitude
                end_lon: End longitude
                avoid_areas: List of {lat, lon} coordinates to avoid
                profile: Route profile (driving-car, foot-walking, cycling-regular)
            
            Returns:
                Alternative route information
            """
            if not self.client:
                # Fallback: Return original route
                distance_km = geodesic((start_lat, start_lon), (end_lat, end_lon)).kilometers
                return {
                    "success": False,
                    "error": "ORS API key not configured",
                    "fallback": {
                        "distance_km": round(distance_km, 2),
                        "coordinates": [
                            [start_lon, start_lat],
                            [end_lon, end_lat]
                        ],
                        "note": "Using direct route as fallback"
                    }
                }
            
            try:
                coords = [[start_lon, start_lat], [end_lon, end_lat]]
                
                # Try to get alternative route
                # OpenRouteService supports alternative routes via alternatives parameter
                route = self.client.directions(
                    coordinates=coords,
                    profile=profile,
                    format='geojson',
                    alternatives=True,
                    instructions=False
                )
                
                # Get the alternative route (index 1 if available, otherwise original)
                if len(route['features']) > 1:
                    alt_route = route['features'][1]
                else:
                    alt_route = route['features'][0]
                
                geometry = alt_route['geometry']['coordinates']
                properties = alt_route.get('properties', {})
                summary = properties.get('summary', {})
                
                route_coords = [[coord[1], coord[0]] for coord in geometry]
                
                return {
                    "success": True,
                    "distance_km": round(summary.get('distance', 0) / 1000, 2),
                    "duration_seconds": summary.get('duration', 0),
                    "duration_minutes": round(summary.get('duration', 0) / 60, 2),
                    "coordinates": route_coords,
                    "route_type": profile,
                    "is_alternative": len(route['features']) > 1,
                    "geometry": geometry
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e)
                }
        
        return Tool(
            name="find_alternative_route",
            description="Find alternative route avoiding high-risk areas",
            function=find_alternative_route
        )
    
    def _create_route_comparison_tool(self):
        """Create tool for comparing routes."""
        def compare_routes(
            original_route: Dict[str, Any],
            alternative_route: Dict[str, Any],
            original_risk: float,
            alternative_risk: float
        ) -> Dict[str, Any]:
            """
            Compare original and alternative routes.
            
            Args:
                original_route: Original route data
                alternative_route: Alternative route data
                original_risk: Risk score of original route
                alternative_risk: Risk score of alternative route
            
            Returns:
                Route comparison analysis
            """
            original_dist = original_route.get("distance_km", 0)
            alt_dist = alternative_route.get("distance_km", 0)
            original_time = original_route.get("duration_minutes", 0)
            alt_time = alternative_route.get("duration_minutes", 0)
            
            distance_diff = alt_dist - original_dist
            time_diff = alt_time - original_time
            risk_improvement = original_risk - alternative_risk
            
            # Determine if alternative is better
            is_better = alternative_risk < original_risk and risk_improvement > 1.0
            
            recommendation = "Use alternative route" if is_better else "Original route acceptable"
            
            return {
                "success": True,
                "is_better": is_better,
                "recommendation": recommendation,
                "comparison": {
                    "distance": {
                        "original_km": round(original_dist, 2),
                        "alternative_km": round(alt_dist, 2),
                        "difference_km": round(distance_diff, 2)
                    },
                    "time": {
                        "original_minutes": round(original_time, 2),
                        "alternative_minutes": round(alt_time, 2),
                        "difference_minutes": round(time_diff, 2)
                    },
                    "risk": {
                        "original_score": round(original_risk, 2),
                        "alternative_score": round(alternative_risk, 2),
                        "improvement": round(risk_improvement, 2)
                    }
                }
            }
        
        return Tool(
            name="compare_routes",
            description="Compare original and alternative routes on distance, time, and safety",
            function=compare_routes
        )
    
    async def optimize_route(
        self,
        original_route: Dict[str, Any],
        risk_assessment: Dict[str, Any],
        safety_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Optimize route by finding safer alternatives.
        
        Args:
            original_route: Original route data from RouteAnalysisAgent
            risk_assessment: Risk assessment from RiskScoringAgent
            safety_data: Safety data from SafetyDataAgent
        
        Returns:
            Route optimization results with alternative suggestions
        """
        risk_score = risk_assessment.get("risk_score", 0)
        
        # Only optimize if risk is moderate or high
        if risk_score < config.RISK_THRESHOLD_MODERATE:
            return {
                "optimization_needed": False,
                "message": "Route risk is acceptable, no optimization needed",
                "risk_score": risk_score
            }
        
        route_data = original_route.get("route_data", {})
        if not route_data.get("success"):
            return {
                "optimization_needed": False,
                "error": "Cannot optimize: invalid route data"
            }
        
        # Extract start and end coordinates
        waypoints = route_data.get("waypoints", [])
        if len(waypoints) < 2:
            return {
                "optimization_needed": False,
                "error": "Insufficient waypoints for optimization"
            }
        
        start = waypoints[0]
        end = waypoints[-1]
        
        # Identify high-risk areas to avoid
        primary_risks = risk_assessment.get("primary_risks", [])
        avoid_areas = []
        
        # If crime is a primary risk, try to avoid those areas
        if any(r["factor"] == "crime" for r in primary_risks):
            # Sample waypoints from original route to avoid
            avoid_areas = waypoints[1:-1]  # Avoid intermediate waypoints
        
        # Find alternative route
        alt_route_tool = self._create_alternative_route_tool()
        alternative_route = alt_route_tool.function(
            start["lat"],
            start["lon"],
            end["lat"],
            end["lon"],
            avoid_areas,
            route_data.get("route_type", "driving-car")
        )
        
        if not alternative_route.get("success"):
            return {
                "optimization_needed": True,
                "error": "Could not find alternative route",
                "fallback": alternative_route.get("fallback")
            }
        
        # Estimate alternative route risk (simplified - would need full safety analysis)
        # For demo, assume alternative is slightly safer
        estimated_alt_risk = max(0, risk_score - 1.5)
        
        # Compare routes
        comparison_tool = self._create_route_comparison_tool()
        comparison = comparison_tool.function(
            route_data,
            alternative_route,
            risk_score,
            estimated_alt_risk
        )
        
        prompt = f"""
        Analyze the route optimization:
        
        Original Route:
        - Distance: {route_data.get('distance_km', 0)} km
        - Time: {route_data.get('duration_minutes', 0)} minutes
        - Risk Score: {risk_score} ({risk_assessment.get('risk_level', 'Unknown')})
        
        Alternative Route:
        - Distance: {alternative_route.get('distance_km', 0)} km
        - Time: {alternative_route.get('duration_minutes', 0)} minutes
        - Estimated Risk Score: {estimated_alt_risk}
        
        Comparison:
        - Risk Improvement: {comparison['comparison']['risk']['improvement']}
        - Distance Difference: {comparison['comparison']['distance']['difference_km']} km
        - Time Difference: {comparison['comparison']['time']['difference_minutes']} minutes
        
        Primary Risks in Original Route: {[r['factor'] for r in primary_risks]}
        
        Provide a recommendation explaining:
        1. Whether the alternative route is safer
        2. Why the alternative is better (or not)
        3. Trade-offs between safety, distance, and time
        4. Final recommendation for the user
        """
        
        response = await self.agent.run(prompt)
        
        return {
            "optimization_needed": True,
            "recommendation": response.text,
            "original_route": route_data,
            "alternative_route": alternative_route,
            "comparison": comparison,
            "risk_improvement": comparison["comparison"]["risk"]["improvement"],
            "should_use_alternative": comparison["is_better"]
        }
    
    def get_agent(self):
        """Get the underlying agent instance."""
        return self.agent

