"""Planner Agent for breaking down study goals into actionable steps."""
from google.ai import agent
from google.generativeai import GenerativeModel
from typing import Dict, Any, List
import config
from tools.custom_tools import StudyPlannerTool


class PlannerAgent:
    """Agent that plans study sessions and breaks down goals into steps."""
    
    def __init__(self, memory_bank=None, session_service=None):
        self.model = GenerativeModel(config.PLANNER_MODEL)
        self.memory_bank = memory_bank
        self.session_service = session_service
        self.study_planner_tool = StudyPlannerTool()
        
        # Create agent with planning instructions
        self.agent = agent.Agent(
            model=self.model,
            instructions="""
            You are a Study Planner Agent. Your role is to:
            1. Break down learning goals into actionable study steps
            2. Create structured study plans with timelines
            3. Prioritize topics based on importance and difficulty
            4. Adapt plans based on user progress and preferences
            
            When creating study plans:
            - Break large goals into smaller, manageable tasks
            - Estimate time needed for each task
            - Consider user's learning pace and preferences
            - Provide clear milestones and checkpoints
            - Suggest optimal study schedules
            
            Always be specific, actionable, and considerate of the user's available time.
            """,
            tools=[self._create_planner_tool()]
        )
    
    def _create_planner_tool(self):
        """Create tool wrapper for study planner."""
        def create_plan(subject: str, goals: List[str], duration_days: int) -> Dict[str, Any]:
            return self.study_planner_tool.create_study_plan(subject, goals, duration_days)
        
        return agent.Tool(
            name="create_study_plan",
            description="Create a structured study plan with goals distributed across days",
            function=create_plan
        )
    
    async def plan_study_session(self, user_goal: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Plan a study session based on user goal.
        
        Args:
            user_goal: The learning goal or topic
            context: Additional context (user preferences, history, etc.)
        
        Returns:
            Structured study plan
        """
        # Get user preferences from memory if available
        user_id = context.get("user_id", "default") if context else "default"
        preferences = {}
        if self.memory_bank:
            preferences = {
                "preferred_format": self.memory_bank.get_user_preference(user_id, "note_format", "markdown"),
                "study_duration": self.memory_bank.get_user_preference(user_id, "study_duration", 7)
            }
        
        prompt = f"""
        Create a detailed study plan for the following goal: {user_goal}
        
        User preferences: {preferences}
        
        Please:
        1. Break down the goal into 3-5 specific learning objectives
        2. Create a timeline for achieving these objectives
        3. Suggest daily study activities
        4. Identify key milestones
        
        Use the create_study_plan tool to generate the structured plan.
        """
        
        response = await self.agent.run(prompt)
        return {
            "plan": response.text,
            "goal": user_goal,
            "preferences": preferences
        }
    
    def get_agent(self):
        """Get the underlying agent instance."""
        return self.agent



