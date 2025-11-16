"""Safety Data Agent for SafeRouteAI - fetches crime, weather, and lighting data."""
from saferouteai.agents.agent_wrapper import Agent, Tool
from google.generativeai import GenerativeModel
from typing import Dict, Any, List
import saferouteai.config as config
import requests
from datetime import datetime, timedelta
import json


class SafetyDataAgent:
    """Agent that fetches real-time safety data: crime, weather, lighting, traffic."""
    
    def __init__(self):
        self.model = GenerativeModel(config.SAFETY_DATA_MODEL)
        
        self.agent = Agent(
            model=self.model,
            instructions="""
            You are a Safety Data Agent. Your role is to:
            1. Fetch real-time weather data for route coordinates
            2. Get crime data near route waypoints
            3. Calculate lighting conditions (sunset/sunrise times)
            4. Assess time-of-day safety factors
            5. Gather traffic and accident data when available
            
            When gathering safety data:
            - Use coordinates from route waypoints
            - Consider current time and date
            - Aggregate data across route segments
            - Provide structured safety indicators
            
            Always provide accurate, real-time safety information.
            """,
            tools=[
                self._create_weather_tool(),
                self._create_lighting_tool(),
                self._create_crime_tool(),
                self._create_time_safety_tool()
            ]
        )
    
    def _create_weather_tool(self):
        """Create tool for weather data."""
        def get_weather(lat: float, lon: float) -> Dict[str, Any]:
            """
            Get current weather conditions for a location.
            
            Args:
                lat: Latitude
                lon: Longitude
            
            Returns:
                Weather data including conditions, temperature, precipitation
            """
            if not config.OPENWEATHER_API_KEY:
                return {
                    "success": False,
                    "error": "OpenWeather API key not configured",
                    "fallback": {
                        "condition": "unknown",
                        "risk_factor": 0.5,
                        "note": "Weather data unavailable"
                    }
                }
            
            try:
                url = f"{config.OPENWEATHER_BASE_URL}/weather"
                params = {
                    "lat": lat,
                    "lon": lon,
                    "appid": config.OPENWEATHER_API_KEY,
                    "units": "metric"
                }
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                weather_main = data.get("weather", [{}])[0].get("main", "").lower()
                temp = data.get("main", {}).get("temp", 20)
                wind_speed = data.get("wind", {}).get("speed", 0)
                visibility = data.get("visibility", 10000) / 1000  # Convert to km
                
                # Calculate weather risk factor
                risk_factors = []
                
                # Rain/storm increases risk
                if weather_main in ["rain", "thunderstorm", "snow", "extreme"]:
                    risk_factors.append(2.0)
                elif weather_main in ["drizzle", "mist", "fog"]:
                    risk_factors.append(1.5)
                
                # Extreme temperatures
                if temp < 0 or temp > 35:
                    risk_factors.append(1.5)
                
                # High wind
                if wind_speed > 15:  # m/s
                    risk_factors.append(1.3)
                
                # Poor visibility
                if visibility < 1:
                    risk_factors.append(2.0)
                elif visibility < 3:
                    risk_factors.append(1.5)
                
                weather_risk = sum(risk_factors) if risk_factors else 0.5
                
                return {
                    "success": True,
                    "condition": weather_main,
                    "temperature_c": round(temp, 1),
                    "wind_speed_ms": round(wind_speed, 1),
                    "visibility_km": round(visibility, 2),
                    "description": data.get("weather", [{}])[0].get("description", ""),
                    "risk_factor": min(weather_risk, 3.0),  # Cap at 3.0
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "fallback": {
                        "condition": "unknown",
                        "risk_factor": 0.5
                    }
                }
        
        return Tool(
            name="get_weather",
            description="Get current weather conditions and calculate weather-related risk factor",
            function=get_weather
        )
    
    def _create_lighting_tool(self):
        """Create tool for sunset/sunrise and lighting conditions."""
        def get_lighting_conditions(lat: float, lon: float, date: str = None) -> Dict[str, Any]:
            """
            Get sunrise/sunset times and current lighting conditions.
            
            Args:
                lat: Latitude
                lon: Longitude
                date: Date in YYYY-MM-DD format (default: today)
            
            Returns:
                Lighting data including sunrise, sunset, and current lighting status
            """
            if date is None:
                date = datetime.now().strftime("%Y-%m-%d")
            
            try:
                url = config.SUNRISE_SUNSET_API
                params = {
                    "lat": lat,
                    "lng": lon,
                    "date": date,
                    "formatted": 0
                }
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                if data.get("status") != "OK":
                    raise Exception("API returned error status")
                
                results = data.get("results", {})
                sunrise_utc = datetime.fromisoformat(results["sunrise"].replace("Z", "+00:00"))
                sunset_utc = datetime.fromisoformat(results["sunset"].replace("Z", "+00:00"))
                
                now = datetime.now()
                # Simple check: if current time is between sunset and sunrise (next day), it's dark
                is_dark = now.hour >= sunset_utc.hour or now.hour < sunrise_utc.hour
                
                # Calculate lighting risk (dark = higher risk)
                lighting_risk = 2.0 if is_dark else 0.5
                
                return {
                    "success": True,
                    "sunrise": sunrise_utc.strftime("%H:%M:%S"),
                    "sunset": sunset_utc.strftime("%H:%M:%S"),
                    "current_time": now.strftime("%H:%M:%S"),
                    "is_dark": is_dark,
                    "lighting_risk": lighting_risk,
                    "date": date
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "fallback": {
                        "is_dark": False,
                        "lighting_risk": 0.5
                    }
                }
        
        return Tool(
            name="get_lighting_conditions",
            description="Get sunrise/sunset times and assess current lighting conditions",
            function=get_lighting_conditions
        )
    
    def _create_crime_tool(self):
        """Create tool for crime data (fallback implementation)."""
        def get_crime_data(lat: float, lon: float, radius_km: float = 1.0) -> Dict[str, Any]:
            """
            Get crime data near a location.
            
            Args:
                lat: Latitude
                lon: Longitude
                radius_km: Search radius in kilometers
            
            Returns:
                Crime data and risk assessment
            """
            # Fallback implementation - in production, integrate with real crime APIs
            # Options: police.uk API, city crime datasets, Kaggle datasets
            
            # For demo purposes, return a simulated risk based on location
            # In production, this would query actual crime databases
            
            crime_risk = 0.5  # Default moderate risk
            
            # Placeholder: You would implement actual crime data fetching here
            # Example: Query police.uk API for UK locations
            # Example: Query city crime datasets for US locations
            # Example: Use Kaggle crime datasets
            
            return {
                "success": True,
                "crime_risk": crime_risk,
                "note": "Using fallback crime assessment. Integrate real crime APIs for production.",
                "radius_km": radius_km,
                "location": {"lat": lat, "lon": lon}
            }
        
        return Tool(
            name="get_crime_data",
            description="Get crime data and risk assessment for a location (fallback implementation)",
            function=get_crime_data
        )
    
    def _create_time_safety_tool(self):
        """Create tool for time-of-day safety assessment."""
        def assess_time_safety(hour: int = None) -> Dict[str, Any]:
            """
            Assess safety based on time of day.
            
            Args:
                hour: Hour of day (0-23), default: current hour
            
            Returns:
                Time-based safety assessment
            """
            if hour is None:
                hour = datetime.now().hour
            
            # Risk increases during late night/early morning
            if 22 <= hour or hour < 6:  # 10 PM - 6 AM
                time_risk = 2.5
                period = "late_night"
            elif 18 <= hour < 22:  # 6 PM - 10 PM
                time_risk = 1.5
                period = "evening"
            elif 6 <= hour < 9 or 17 <= hour < 18:  # Rush hours
                time_risk = 1.2
                period = "rush_hour"
            else:  # Daytime
                time_risk = 0.5
                period = "daytime"
            
            return {
                "success": True,
                "hour": hour,
                "period": period,
                "time_risk": time_risk,
                "timestamp": datetime.now().isoformat()
            }
        
        return Tool(
            name="assess_time_safety",
            description="Assess safety risk based on time of day",
            function=assess_time_safety
        )
    
    async def gather_safety_data(self, route_coordinates: List[List[float]]) -> Dict[str, Any]:
        """
        Gather safety data for all route waypoints.
        
        Args:
            route_coordinates: List of [lat, lon] coordinates along route
        
        Returns:
            Aggregated safety data
        """
        # Sample waypoints (use every Nth coordinate to avoid too many API calls)
        sample_size = min(5, len(route_coordinates))
        step = max(1, len(route_coordinates) // sample_size)
        sampled_coords = route_coordinates[::step]
        
        weather_data = []
        lighting_data = []
        crime_data = []
        time_data = []
        
        for coord in sampled_coords:
            lat, lon = coord[0], coord[1]
            
            # Get weather
            weather = self._create_weather_tool().function(lat, lon)
            if weather.get("success"):
                weather_data.append(weather)
            
            # Get lighting (only once, same for all points)
            if not lighting_data:
                lighting = self._create_lighting_tool().function(lat, lon)
                if lighting.get("success"):
                    lighting_data.append(lighting)
            
            # Get crime data
            crime = self._create_crime_tool().function(lat, lon)
            crime_data.append(crime)
            
            # Get time safety (only once)
            if not time_data:
                time_safety = self._create_time_safety_tool().function()
                time_data.append(time_safety)
        
        # Aggregate data
        avg_weather_risk = sum(w.get("risk_factor", 0.5) for w in weather_data) / len(weather_data) if weather_data else 0.5
        avg_crime_risk = sum(c.get("crime_risk", 0.5) for c in crime_data) / len(crime_data) if crime_data else 0.5
        lighting_risk = lighting_data[0].get("lighting_risk", 0.5) if lighting_data else 0.5
        time_risk = time_data[0].get("time_risk", 0.5) if time_data else 0.5
        
        prompt = f"""
        Analyze the safety data gathered for the route:
        - Weather risk: {avg_weather_risk}
        - Crime risk: {avg_crime_risk}
        - Lighting risk: {lighting_risk}
        - Time risk: {time_risk}
        
        Provide a summary of safety factors affecting this route.
        """
        
        response = await self.agent.run(prompt)
        
        return {
            "summary": response.text,
            "weather_data": weather_data,
            "lighting_data": lighting_data[0] if lighting_data else {},
            "crime_data": crime_data,
            "time_data": time_data[0] if time_data else {},
            "aggregated_risks": {
                "weather": avg_weather_risk,
                "crime": avg_crime_risk,
                "lighting": lighting_risk,
                "time": time_risk
            }
        }
    
    def get_agent(self):
        """Get the underlying agent instance."""
        return self.agent

