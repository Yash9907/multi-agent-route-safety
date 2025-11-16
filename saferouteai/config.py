"""Configuration file for SafeRouteAI system."""
import os
from dotenv import load_dotenv

load_dotenv()

# Google AI API Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# OpenRouteService API Configuration (Free tier: https://openrouteservice.org/)
ORS_API_KEY = os.getenv("ORS_API_KEY", "")

# OpenWeather API Configuration (Free tier: https://openweathermap.org/api)
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")

# Agent Configuration
ROUTE_ANALYSIS_MODEL = "gemini-2.0-flash-exp"
SAFETY_DATA_MODEL = "gemini-2.0-flash-exp"
RISK_SCORING_MODEL = "gemini-2.0-flash-exp"
ROUTE_OPTIMIZATION_MODEL = "gemini-2.0-flash-exp"
ALERT_MODEL = "gemini-2.0-flash-exp"

# API Endpoints
ORS_BASE_URL = "https://api.openrouteservice.org/v2"
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"
SUNRISE_SUNSET_API = "https://api.sunrise-sunset.org/json"

# Risk Scoring Configuration
RISK_THRESHOLD_MODERATE = 4
RISK_THRESHOLD_HAZARDOUS = 7
RISK_MAX_SCORE = 10

# Crime Data Sources (fallback options)
# USA: Use city/state crime datasets
# UK: police.uk API
# Other: Kaggle crime datasets or Google Places API
CRIME_DATA_SOURCE = os.getenv("CRIME_DATA_SOURCE", "fallback")  # Options: "police_uk", "city_data", "kaggle", "fallback"

# Logging Configuration
LOG_LEVEL = "INFO"
ENABLE_TRACING = True



