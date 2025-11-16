"""Alert Agent for SafeRouteAI - provides human-readable safety guidance."""
from saferouteai.agents.agent_wrapper import Agent, Tool
from google.generativeai import GenerativeModel
from typing import Dict, Any
import saferouteai.config as config
from datetime import datetime


class AlertAgent:
    """Agent that generates clear, human-readable safety alerts and guidance."""
    
    def __init__(self):
        self.model = GenerativeModel(config.ALERT_MODEL)
        
        self.agent = Agent(
            model=self.model,
            instructions="""
            You are an Alert Agent. Your role is to:
            1. Generate clear, actionable safety alerts for users
            2. Translate technical risk scores into plain language
            3. Provide specific safety recommendations
            4. Create urgency-appropriate warnings
            5. Format alerts for easy reading
            
            Alert Guidelines:
            - Use clear, non-technical language
            - Be specific about risks (e.g., "heavy rain expected" not "weather risk")
            - Provide actionable advice (e.g., "avoid this route after 10 PM")
            - Match alert severity to risk level
            - Include relevant safety tips
            
            Always prioritize user safety and clarity.
            """,
            tools=[self._create_alert_formatter_tool()]
        )
    
    def _create_alert_formatter_tool(self):
        """Create tool for formatting alerts."""
        def format_alert(
            risk_level: str,
            risk_score: float,
            primary_risks: list,
            recommendation: str,
            route_info: Dict[str, Any] = None
        ) -> Dict[str, Any]:
            """
            Format safety alert with appropriate severity and messaging.
            
            Args:
                risk_level: Risk level (Safe, Moderate, Hazardous)
                risk_score: Numeric risk score (0-10)
                primary_risks: List of primary risk factors
                recommendation: General recommendation
                route_info: Optional route information
            
            Returns:
                Formatted alert with severity, message, and actions
            """
            # Determine alert severity
            if risk_level == "Hazardous":
                severity = "high"
                icon = "⚠️"
                urgency = "immediate"
            elif risk_level == "Moderate":
                severity = "medium"
                icon = "⚡"
                urgency = "caution"
            else:
                severity = "low"
                icon = "✅"
                urgency = "informational"
            
            # Build risk factors list
            risk_factors_text = ", ".join([
                f"{r['factor']} (score: {r['score']})"
                for r in primary_risks
            ])
            
            # Generate alert message
            if severity == "high":
                message = f"{icon} HIGH RISK ALERT: This route has significant safety concerns."
                actions = [
                    "Consider delaying travel if possible",
                    "Use alternative route if available",
                    "Travel with others if necessary",
                    "Stay alert and avoid distractions"
                ]
            elif severity == "medium":
                message = f"{icon} MODERATE RISK: Exercise caution on this route."
                actions = [
                    "Be aware of your surroundings",
                    "Stay in well-lit areas",
                    "Keep phone charged and accessible",
                    "Consider alternative route if convenient"
                ]
            else:
                message = f"{icon} Route appears safe for travel."
                actions = [
                    "Standard safety precautions apply",
                    "Stay aware of changing conditions"
                ]
            
            # Add route-specific info if available
            route_details = ""
            if route_info:
                distance = route_info.get("distance_km", 0)
                duration = route_info.get("duration_minutes", 0)
                route_details = f"\nRoute: {distance} km, ~{duration} minutes"
            
            return {
                "success": True,
                "severity": severity,
                "urgency": urgency,
                "icon": icon,
                "message": message,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "risk_factors": risk_factors_text,
                "primary_risks": primary_risks,
                "recommendation": recommendation,
                "actions": actions,
                "route_details": route_details,
                "timestamp": datetime.now().isoformat(),
                "formatted_alert": f"""
{message}

Risk Score: {risk_score}/10 ({risk_level})
Primary Concerns: {risk_factors_text}
{route_details}

Recommendation: {recommendation}

Safety Actions:
{chr(10).join(f"• {action}" for action in actions)}
                """.strip()
            }
        
        return Tool(
            name="format_alert",
            description="Format safety alert with appropriate severity, message, and actions",
            function=format_alert
        )
    
    async def generate_alert(
        self,
        risk_assessment: Dict[str, Any],
        route_data: Dict[str, Any] = None,
        optimization_result: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate human-readable safety alert.
        
        Args:
            risk_assessment: Risk assessment from RiskScoringAgent
            route_data: Optional route data from RouteAnalysisAgent
            optimization_result: Optional optimization result from RouteOptimizationAgent
        
        Returns:
            Formatted safety alert
        """
        risk_level = risk_assessment.get("risk_level", "Unknown")
        risk_score = risk_assessment.get("risk_score", 0)
        primary_risks = risk_assessment.get("primary_risks", [])
        recommendation = risk_assessment.get("recommendation", "")
        
        route_info = None
        if route_data:
            route_info = route_data.get("route_data", {})
        
        # Format alert
        alert_tool = self._create_alert_formatter_tool()
        formatted_alert = alert_tool.function(
            risk_level,
            risk_score,
            primary_risks,
            recommendation,
            route_info
        )
        
        # Generate detailed guidance
        optimization_note = ""
        if optimization_result and optimization_result.get("optimization_needed"):
            if optimization_result.get("should_use_alternative"):
                optimization_note = f"""
                
Alternative Route Available:
An alternative route has been identified that may be safer:
- Risk improvement: {optimization_result.get('risk_improvement', 0):.2f} points
- Distance difference: {optimization_result['comparison']['comparison']['distance']['difference_km']:.2f} km
- Time difference: {optimization_result['comparison']['comparison']['time']['difference_minutes']:.2f} minutes

{optimization_result.get('recommendation', '')}
                """
        
        prompt = f"""
        Generate a comprehensive safety alert for the user based on:
        
        Risk Assessment:
        - Risk Level: {risk_level}
        - Risk Score: {risk_score}/10
        - Primary Risks: {[r['factor'] for r in primary_risks]}
        - Recommendation: {recommendation}
        
        {optimization_note if optimization_note else ''}
        
        Create a clear, actionable safety alert that:
        1. Explains the risk in plain language
        2. Identifies specific concerns (weather, crime, lighting, time)
        3. Provides practical safety advice
        4. Recommends next steps
        5. Is easy to understand and act upon
        
        Format the alert as a user-friendly message.
        """
        
        response = await self.agent.run(prompt)
        
        return {
            "alert": formatted_alert,
            "detailed_guidance": response.text,
            "risk_assessment": risk_assessment,
            "optimization_available": optimization_result is not None and optimization_result.get("optimization_needed", False)
        }
    
    def get_agent(self):
        """Get the underlying agent instance."""
        return self.agent

