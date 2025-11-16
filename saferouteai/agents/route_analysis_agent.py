"""Route Analysis Agent for SafeRouteAI."""
from saferouteai.agents.agent_wrapper import Agent, Tool
from google.generativeai import GenerativeModel
from typing import Dict, Any, List, Tuple
import saferouteai.config as config
import openrouteservice
from geopy.distance import geodesic


class RouteAnalysisAgent:
    """Agent that analyzes routes and extracts route information."""
    
    def __init__(self):
        self.model = GenerativeModel(config.ROUTE_ANALYSIS_MODEL)
        self.client = openrouteservice.Client(key=config.ORS_API_KEY) if config.ORS_API_KEY else None
        
        self.agent = Agent(
            model=self.model,
            instructions="""
            You are a Route Analysis Agent. Your role is to:
            1. Analyze routes between start and destination points
            2. Extract route coordinates, distance, and duration
            3. Identify waypoints and route segments
            4. Provide route geometry for safety analysis
            
            When analyzing routes:
            - Extract all coordinates along the route
            - Calculate total distance and estimated travel time
            - Identify key waypoints and intersections
            - Note route type (walking, driving, cycling)
            - Provide route segments for granular safety analysis
            
            Always provide clear, structured route information.
            """,
            tools=[self._create_route_tool()]
        )
    
    def _create_route_tool(self):
        """Create tool for route planning."""
        def get_route(start_lat: float, start_lon: float, 
                     end_lat: float, end_lon: float, 
                     profile: str = "driving-car") -> Dict[str, Any]:
            """
            Get route from start to destination.
            
            Args:
                start_lat: Start latitude
                start_lon: Start longitude
                end_lat: End latitude
                end_lon: End longitude
                profile: Route profile (driving-car, foot-walking, cycling-regular)
            
            Returns:
                Route information with coordinates, distance, duration
            """
            if not self.client:
                # Fallback: Calculate straight-line distance
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
                        "waypoints": [
                            {"lat": start_lat, "lon": start_lon, "name": "Start"},
                            {"lat": end_lat, "lon": end_lon, "name": "Destination"}
                        ]
                    }
                }
            
            try:
                coords = [[start_lon, start_lat], [end_lon, end_lat]]
                route = self.client.directions(
                    coordinates=coords,
                    profile=profile,
                    format='geojson'
                )
                
                # Extract route information
                geometry = route['features'][0]['geometry']['coordinates']
                properties = route['features'][0]['properties']
                summary = properties.get('summary', {})
                
                # Convert coordinates to [lat, lon] format
                route_coords = [[coord[1], coord[0]] for coord in geometry]
                
                return {
                    "success": True,
                    "distance_km": round(summary.get('distance', 0) / 1000, 2),
                    "duration_seconds": summary.get('duration', 0),
                    "duration_minutes": round(summary.get('duration', 0) / 60, 2),
                    "coordinates": route_coords,
                    "waypoints": self._extract_waypoints(route_coords),
                    "route_type": profile,
                    "geometry": geometry
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e)
                }
        
        return Tool(
            name="get_route",
            description="Get route between two points with coordinates, distance, and waypoints",
            function=get_route
        )
    
    def _extract_waypoints(self, coordinates: List[List[float]], max_points: int = 10) -> List[Dict[str, Any]]:
        """Extract key waypoints from route coordinates."""
        if len(coordinates) <= max_points:
            return [{"lat": coord[0], "lon": coord[1], "index": i} 
                   for i, coord in enumerate(coordinates)]
        
        # Sample evenly spaced waypoints
        step = len(coordinates) // max_points
        waypoints = []
        for i in range(0, len(coordinates), step):
            waypoints.append({
                "lat": coordinates[i][0],
                "lon": coordinates[i][1],
                "index": i
            })
        
        # Always include start and end
        if waypoints[-1]["index"] != len(coordinates) - 1:
            waypoints.append({
                "lat": coordinates[-1][0],
                "lon": coordinates[-1][1],
                "index": len(coordinates) - 1
            })
        
        return waypoints
    
    async def analyze_route(self, start: str, destination: str, 
                           route_type: str = "driving-car") -> Dict[str, Any]:
        """
        Analyze route from start to destination.
        
        Args:
            start: Start location (address or "lat,lon")
            destination: Destination location (address or "lat,lon")
            route_type: Type of route (driving-car, foot-walking, cycling-regular)
        
        Returns:
            Route analysis with coordinates and metadata
        """
        # For now, assume coordinates are provided as "lat,lon"
        # In production, you'd geocode addresses here
        try:
            start_lat, start_lon = map(float, start.split(','))
            end_lat, end_lon = map(float, destination.split(','))
        except:
            return {
                "success": False,
                "error": "Invalid coordinate format. Use 'lat,lon'"
            }
        
        prompt = f"""
        Analyze the route from {start} to {destination}.
        
        Use the get_route tool to:
        1. Get the route coordinates
        2. Extract distance and duration
        3. Identify waypoints for safety analysis
        
        Route type: {route_type}
        """
        
        response = await self.agent.run(prompt)
        
        # Get route data from tool
        route_data = self._create_route_tool().function(
            start_lat, start_lon, end_lat, end_lon, route_type
        )
        
        return {
            "analysis": response.text,
            "route_data": route_data,
            "start": start,
            "destination": destination,
            "route_type": route_type
        }
    
    def get_agent(self):
        """Get the underlying agent instance."""
        return self.agent

