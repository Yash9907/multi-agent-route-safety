"""Custom tools for EduMentor agents."""
from typing import Dict, List, Any
from google.ai import agent
import json
import os
from datetime import datetime


class NoteGeneratorTool:
    """Tool for generating structured study notes."""
    
    def __init__(self, output_dir: str = "./notes"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_notes(self, topic: str, content: str, format_type: str = "markdown") -> Dict[str, Any]:
        """
        Generate structured study notes from content.
        
        Args:
            topic: The topic/subject of the notes
            content: The content to convert into notes
            format_type: Format of notes (markdown, bullet, outline)
        
        Returns:
            Dictionary with note content and metadata
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{topic.replace(' ', '_')}_{timestamp}.md"
        filepath = os.path.join(self.output_dir, filename)
        
        # Structure notes based on format
        if format_type == "markdown":
            note_content = f"# {topic}\n\n## Summary\n{content}\n\n## Key Points\n- Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        elif format_type == "bullet":
            note_content = f"# {topic}\n\n{content}\n\n## Quick Reference\n- Study Date: {datetime.now().strftime('%Y-%m-%d')}\n"
        else:  # outline
            note_content = f"# {topic}\n\n## Outline\n{content}\n"
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(note_content)
        
        return {
            "success": True,
            "topic": topic,
            "filepath": filepath,
            "content": note_content,
            "format": format_type,
            "timestamp": timestamp
        }
    
    def get_tool_spec(self) -> Dict[str, Any]:
        """Get tool specification for agent SDK."""
        return {
            "name": "generate_notes",
            "description": "Generate structured study notes from content. Supports markdown, bullet, and outline formats.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "The topic or subject of the notes"
                    },
                    "content": {
                        "type": "string",
                        "description": "The content to convert into structured notes"
                    },
                    "format_type": {
                        "type": "string",
                        "enum": ["markdown", "bullet", "outline"],
                        "description": "Format type for the notes",
                        "default": "markdown"
                    }
                },
                "required": ["topic", "content"]
            }
        }


class QuizGeneratorTool:
    """Tool for generating quizzes and assessments."""
    
    def __init__(self, output_dir: str = "./quizzes"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_quiz(self, topic: str, questions: List[Dict[str, Any]], difficulty: str = "medium") -> Dict[str, Any]:
        """
        Generate a quiz from questions.
        
        Args:
            topic: The topic of the quiz
            questions: List of question dictionaries with 'question', 'options', 'correct_answer'
            difficulty: Difficulty level (easy, medium, hard)
        
        Returns:
            Dictionary with quiz content and metadata
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"quiz_{topic.replace(' ', '_')}_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        quiz_data = {
            "topic": topic,
            "difficulty": difficulty,
            "questions": questions,
            "total_questions": len(questions),
            "created_at": datetime.now().isoformat()
        }
        
        # Save quiz
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(quiz_data, f, indent=2, ensure_ascii=False)
        
        # Generate formatted quiz text
        quiz_text = f"# Quiz: {topic}\n\nDifficulty: {difficulty}\n\n"
        for i, q in enumerate(questions, 1):
            quiz_text += f"## Question {i}\n{q['question']}\n\n"
            if 'options' in q:
                for j, opt in enumerate(q['options'], 1):
                    quiz_text += f"{j}. {opt}\n"
            quiz_text += "\n"
        
        return {
            "success": True,
            "topic": topic,
            "filepath": filepath,
            "quiz_data": quiz_data,
            "formatted_text": quiz_text,
            "total_questions": len(questions)
        }
    
    def get_tool_spec(self) -> Dict[str, Any]:
        """Get tool specification for agent SDK."""
        return {
            "name": "generate_quiz",
            "description": "Generate quizzes with multiple choice questions. Returns quiz data and formatted text.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "The topic of the quiz"
                    },
                    "questions": {
                        "type": "array",
                        "description": "List of question objects with 'question', 'options', and 'correct_answer'",
                        "items": {
                            "type": "object",
                            "properties": {
                                "question": {"type": "string"},
                                "options": {"type": "array", "items": {"type": "string"}},
                                "correct_answer": {"type": "integer"}
                            }
                        }
                    },
                    "difficulty": {
                        "type": "string",
                        "enum": ["easy", "medium", "hard"],
                        "default": "medium"
                    }
                },
                "required": ["topic", "questions"]
            }
        }


class StudyPlannerTool:
    """Tool for creating study plans and schedules."""
    
    def create_study_plan(self, subject: str, goals: List[str], duration_days: int) -> Dict[str, Any]:
        """
        Create a structured study plan.
        
        Args:
            subject: The subject to study
            goals: List of learning goals
            duration_days: Number of days for the study plan
        
        Returns:
            Dictionary with study plan structure
        """
        plan = {
            "subject": subject,
            "goals": goals,
            "duration_days": duration_days,
            "created_at": datetime.now().isoformat(),
            "schedule": []
        }
        
        # Distribute goals across duration
        days_per_goal = max(1, duration_days // len(goals))
        for i, goal in enumerate(goals):
            start_day = i * days_per_goal + 1
            end_day = min((i + 1) * days_per_goal, duration_days)
            plan["schedule"].append({
                "goal": goal,
                "day_range": f"{start_day}-{end_day}",
                "status": "pending"
            })
        
        return {
            "success": True,
            "plan": plan,
            "total_goals": len(goals)
        }
    
    def get_tool_spec(self) -> Dict[str, Any]:
        """Get tool specification for agent SDK."""
        return {
            "name": "create_study_plan",
            "description": "Create a structured study plan with goals distributed across days.",
            "parameters": {
                "type": "object",
                "properties": {
                    "subject": {
                        "type": "string",
                        "description": "The subject to study"
                    },
                    "goals": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of learning goals"
                    },
                    "duration_days": {
                        "type": "integer",
                        "description": "Number of days for the study plan"
                    }
                },
                "required": ["subject", "goals", "duration_days"]
            }
        }



