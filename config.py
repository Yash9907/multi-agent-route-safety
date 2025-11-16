"""Configuration file for EduMentor system."""
import os
from dotenv import load_dotenv

load_dotenv()

# Google AI API Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# Agent Configuration
PLANNER_MODEL = "gemini-2.0-flash-exp"
TEACHER_MODEL = "gemini-2.0-flash-exp"
EVALUATOR_MODEL = "gemini-2.0-flash-exp"

# Memory Configuration
MEMORY_BANK_PATH = "./memory_bank"
SESSION_STORAGE_PATH = "./sessions"

# Observability Configuration
LOG_LEVEL = "INFO"
ENABLE_TRACING = True
ENABLE_METRICS = True



