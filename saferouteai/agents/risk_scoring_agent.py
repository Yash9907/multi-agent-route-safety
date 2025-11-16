"""Risk Scoring Agent for SafeRouteAI - computes combined risk scores."""
from saferouteai.agents.agent_wrapper import Agent, Tool
from google.generativeai import GenerativeModel
from typing import Dict, Any, List
import saferouteai.config as config
import json


class RiskScoringAgent:
    """Agent that computes combined risk scores from multiple safety factors."""
    
    def __init__(self):
        self.model = GenerativeModel(config.RISK_SCORING_MODEL)
        
        self.agent = Agent(
            model=self.model,
            instructions="""
            You are a Risk Scoring Agent. Your role is to:
            1. Analyze aggregated safety data (weather, crime, lighting, time)
            2. Compute a combined risk score on a scale of 0-10
            3. Categorize risk levels:
               - 0-3: Safe
               - 4-6: Moderate
               - 7-10: Hazardous
            4. Identify primary risk factors
            5. Provide risk breakdown by category
            
            Risk Scoring Formula:
            - Base risk starts at 0
            - Weather risk: 0-3 points (severe weather = higher)
            - Crime risk: 0-3 points (high crime areas = higher)
            - Lighting risk: 0-2 points (dark = higher)
            - Time risk: 0-2 points (late night = higher)
            - Total capped at 10
            
            Always provide clear, justified risk assessments.
            """,
            tools=[self._create_risk_calculator_tool()]
        )
    
    def _create_risk_calculator_tool(self):
        """Create tool for calculating risk scores."""
        def calculate_risk_score(
            weather_risk: float,
            crime_risk: float,
            lighting_risk: float,
            time_risk: float
        ) -> Dict[str, Any]:
            """
            Calculate combined risk score from individual risk factors.
            
            Args:
                weather_risk: Weather-related risk (0-3)
                crime_risk: Crime-related risk (0-3)
                lighting_risk: Lighting-related risk (0-2)
                time_risk: Time-of-day risk (0-2)
            
            Returns:
                Comprehensive risk assessment with score and breakdown
            """
            # Normalize and weight risk factors
            weather_weighted = min(weather_risk * 1.0, 3.0)
            crime_weighted = min(crime_risk * 1.0, 3.0)
            lighting_weighted = min(lighting_risk * 1.0, 2.0)
            time_weighted = min(time_risk * 1.0, 2.0)
            
            # Calculate total risk score
            total_risk = weather_weighted + crime_weighted + lighting_weighted + time_weighted
            total_risk = min(total_risk, 10.0)  # Cap at 10
            
            # Determine risk level
            if total_risk <= 3:
                risk_level = "Safe"
                risk_category = "low"
            elif total_risk <= 6:
                risk_level = "Moderate"
                risk_category = "medium"
            else:
                risk_level = "Hazardous"
                risk_category = "high"
            
            # Identify primary risk factors
            risk_factors = {
                "weather": weather_weighted,
                "crime": crime_weighted,
                "lighting": lighting_weighted,
                "time": time_weighted
            }
            primary_risks = sorted(
                risk_factors.items(),
                key=lambda x: x[1],
                reverse=True
            )[:2]  # Top 2 risk factors
            
            return {
                "success": True,
                "total_risk_score": round(total_risk, 2),
                "risk_level": risk_level,
                "risk_category": risk_category,
                "risk_breakdown": {
                    "weather": round(weather_weighted, 2),
                    "crime": round(crime_weighted, 2),
                    "lighting": round(lighting_weighted, 2),
                    "time": round(time_weighted, 2)
                },
                "primary_risks": [
                    {"factor": factor, "score": round(score, 2)}
                    for factor, score in primary_risks
                ],
                "recommendation": (
                    "Route is safe to travel" if risk_category == "low" else
                    "Exercise caution" if risk_category == "medium" else
                    "Consider alternative route or delay travel"
                )
            }
        
        return Tool(
            name="calculate_risk_score",
            description="Calculate combined risk score from weather, crime, lighting, and time factors",
            function=calculate_risk_score
        )
    
    async def score_route_risk(
        self,
        safety_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Score route risk based on safety data.
        
        Args:
            safety_data: Aggregated safety data from SafetyDataAgent
        
        Returns:
            Risk assessment with score and recommendations
        """
        aggregated_risks = safety_data.get("aggregated_risks", {})
        
        weather_risk = aggregated_risks.get("weather", 0.5)
        crime_risk = aggregated_risks.get("crime", 0.5)
        lighting_risk = aggregated_risks.get("lighting", 0.5)
        time_risk = aggregated_risks.get("time", 0.5)
        
        # Calculate risk score
        risk_result = self._create_risk_calculator_tool().function(
            weather_risk,
            crime_risk,
            lighting_risk,
            time_risk
        )
        
        prompt = f"""
        Analyze the route risk based on the following safety data:
        
        Weather Risk: {weather_risk}
        Crime Risk: {crime_risk}
        Lighting Risk: {lighting_risk}
        Time Risk: {time_risk}
        
        Total Risk Score: {risk_result['total_risk_score']}
        Risk Level: {risk_result['risk_level']}
        
        Provide a detailed risk assessment explaining:
        1. Why the route received this risk score
        2. What factors contribute most to the risk
        3. Specific safety concerns for this route
        4. Whether the route should be avoided or if caution is sufficient
        """
        
        response = await self.agent.run(prompt)
        
        return {
            "risk_assessment": response.text,
            "risk_score": risk_result["total_risk_score"],
            "risk_level": risk_result["risk_level"],
            "risk_category": risk_result["risk_category"],
            "risk_breakdown": risk_result["risk_breakdown"],
            "primary_risks": risk_result["primary_risks"],
            "recommendation": risk_result["recommendation"],
            "safety_data_summary": safety_data.get("summary", "")
        }
    
    def get_agent(self):
        """Get the underlying agent instance."""
        return self.agent

