"""Teacher Agent for generating explanations, summaries, and study materials."""
from google.ai import agent
from google.generativeai import GenerativeModel
from typing import Dict, Any
import config
from tools.custom_tools import NoteGeneratorTool


class TeacherAgent:
    """Agent that teaches concepts and generates study materials."""
    
    def __init__(self, memory_bank=None, session_service=None):
        self.model = GenerativeModel(config.TEACHER_MODEL)
        self.memory_bank = memory_bank
        self.session_service = session_service
        self.note_generator = NoteGeneratorTool()
        
        # Create agent with teaching instructions
        self.agent = agent.Agent(
            model=self.model,
            instructions="""
            You are a Teacher Agent. Your role is to:
            1. Explain concepts clearly and adaptively
            2. Generate comprehensive study notes and summaries
            3. Create flashcards and quick reference materials
            4. Break down complex topics into digestible parts
            5. Use analogies and examples to enhance understanding
            
            When teaching:
            - Start with fundamentals and build up complexity
            - Use clear, concise language appropriate for the learner's level
            - Include examples and real-world applications
            - Highlight key concepts and important details
            - Create well-structured notes that are easy to review
            
            Always be encouraging and supportive. Adapt your teaching style to the user's needs.
            """,
            tools=[self._create_note_tool()]
        )
    
    def _create_note_tool(self):
        """Create tool wrapper for note generator."""
        def generate_notes(topic: str, content: str, format_type: str = "markdown") -> Dict[str, Any]:
            return self.note_generator.generate_notes(topic, content, format_type)
        
        return agent.Tool(
            name="generate_notes",
            description="Generate structured study notes from content. Supports markdown, bullet, and outline formats.",
            function=generate_notes
        )
    
    async def teach_topic(self, topic: str, level: str = "intermediate", context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Teach a topic and generate study materials.
        
        Args:
            topic: The topic to teach
            level: Learning level (beginner, intermediate, advanced)
            context: Additional context (previous knowledge, preferences, etc.)
        
        Returns:
            Teaching content and generated notes
        """
        # Get user preferences
        user_id = context.get("user_id", "default") if context else "default"
        preferred_format = "markdown"
        if self.memory_bank:
            preferred_format = self.memory_bank.get_user_preference(user_id, "note_format", "markdown")
        
        # Get existing knowledge about topic
        existing_knowledge = {}
        if self.memory_bank:
            existing_knowledge = self.memory_bank.get_topic_knowledge(topic)
        
        prompt = f"""
        Teach the topic: {topic}
        
        Learning level: {level}
        Existing knowledge: {existing_knowledge}
        
        Please:
        1. Provide a clear explanation of the topic
        2. Break it down into key concepts
        3. Include examples and applications
        4. Generate structured study notes using the generate_notes tool
        
        Make the explanation engaging and easy to understand.
        """
        
        response = await self.agent.run(prompt)
        
        # Store knowledge in memory bank
        if self.memory_bank:
            self.memory_bank.store_topic_knowledge(topic, {
                "level": level,
                "taught_at": context.get("timestamp") if context else None
            })
        
        return {
            "explanation": response.text,
            "topic": topic,
            "level": level,
            "notes_generated": True
        }
    
    def get_agent(self):
        """Get the underlying agent instance."""
        return self.agent



