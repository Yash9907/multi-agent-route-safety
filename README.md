# SafeRouteAI – Multi-Agent Real-Time Route Safety Advisor

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue" />
  <img src="https://img.shields.io/badge/AI-Multi--Agent System-green" />
  <img src="https://img.shields.io/badge/Google AI-Agent SDK-orange" />
  <img src="https://img.shields.io/badge/Status-Active-brightgreen" />
  <img src="https://img.shields.io/badge/License-MIT-lightgrey" />
</p>


A multi-agent AI system that analyzes route safety in real-time by combining crime data, weather conditions, traffic, time of day, and lighting conditions to provide safety recommendations.

## 🌟 Project Overview

SafeRouteAI is an autonomous multi-agent system built with Google AI Agent SDK that evaluates the safety of walking/driving routes by analyzing multiple risk factors and recommending safer alternatives when needed.

### Key Features

- **Multi-Agent System**: 5 specialized agents working together
- **Real-Time Analysis**: Weather, crime, lighting, and time-based risk assessment
- **Route Optimization**: Suggests safer alternative routes
- **Memory & Sessions**: Remembers user preferences and route history
- **Observability**: Comprehensive logging and tracing
- **Parallel Processing**: Batch route analysis support

## 🏗️ System Architecture

### Agent Architecture

1. **Route Analysis Agent**: Extracts route coordinates, distance, and waypoints
2. **Safety Data Agent**: Gathers weather, crime, lighting, and time-of-day data
3. **Risk Scoring Agent**: Computes combined risk scores (0-10 scale)
4. **Route Optimization Agent**: Suggests safer alternatives for high-risk routes
5. **Alert Agent**: Generates human-readable safety guidance

### Multi-Agent Patterns

- **Sequential Agents**: Route Analysis → Safety Data → Risk Scoring → Alert
- **Parallel Agents**: Batch route analysis with concurrent processing
- **Conditional Agents**: Route Optimization only triggers for moderate/high risk routes
- **Loop Agents**: Session memory maintains history across multiple analyses

## 🛠️ Tools & APIs

### Custom Tools

- **Route Planning Tool**: OpenRouteService integration for route calculation
- **Weather Tool**: OpenWeather API for real-time weather conditions
- **Lighting Tool**: Sunrise-sunset API for daylight assessment
- **Crime Data Tool**: Fallback crime risk assessment (extensible for real APIs)
- **Time Safety Tool**: Time-of-day risk calculation
- **Risk Calculator Tool**: Combined risk score computation
- **Route Comparison Tool**: Compare original vs alternative routes
- **Alert Formatter Tool**: Format safety alerts with appropriate severity

### External APIs

- **OpenRouteService**: Free tier routing API
- **OpenWeather**: Free tier weather API
- **Sunrise-Sunset API**: Free daylight times API
- **Crime Data**: Extensible for police.uk, city datasets, or Kaggle datasets

## 📋 Requirements

### Key Concepts Implemented

✅ **Multi-Agent System**
- Agent powered by LLM (Gemini 2.0 Flash)
- Sequential agents (pipeline pattern)
- Parallel agents (batch processing)
- Conditional agents (optimization only when needed)

✅ **Tools**
- Custom tools (route, weather, lighting, crime, risk calculation)
- Built-in tools (Google Search available via SDK)
- OpenAPI tools (OpenRouteService, OpenWeather)

✅ **Sessions & Memory**
- InMemorySessionService (session_manager.py)
- Long-term memory (route history, user preferences)
- Context engineering (session-based state management)

✅ **Observability**
- Logging (file and console handlers)
- Tracing (operation timing and context)
- Metrics (operation statistics)

## 🚀 Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd "capstone project"
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env and add your API keys
```

4. **Get API Keys** (all free tiers available):
   - **Google AI**: https://aistudio.google.com/apikey
   - **OpenRouteService**: https://openrouteservice.org/dev/#/signup
   - **OpenWeather**: https://openweathermap.org/api

## 💻 Usage

### Basic Usage

```python
import asyncio
from saferouteai import SafeRouteOrchestrator

async def main():
    orchestrator = SafeRouteOrchestrator(session_id="my_session")
    
    result = await orchestrator.analyze_route_safety(
        start="37.7749,-122.4194",  # San Francisco
        destination="37.6213,-122.3790",  # SFO Airport
        route_type="driving-car"
    )
    
    print(f"Risk Score: {result['summary']['risk_score']}/10")
    print(f"Risk Level: {result['summary']['risk_level']}")
    print(result['safety_alert']['alert']['formatted_alert'])

asyncio.run(main())
```

### Run Demo

```bash
python demo.py
```

The demo showcases:
1. Single route analysis
2. Batch route analysis (parallel agents)
3. Memory and user preferences
4. Observability features

## 📊 Risk Scoring

Risk scores are calculated on a 0-10 scale:

- **0-3: Safe** - Route is safe to travel
- **4-6: Moderate** - Exercise caution
- **7-10: Hazardous** - Consider alternative route or delay travel

### Risk Factors

- **Weather Risk** (0-3): Rain, storms, extreme temperatures, poor visibility
- **Crime Risk** (0-3): Crime data near route (extensible for real APIs)
- **Lighting Risk** (0-2): Dark hours increase risk
- **Time Risk** (0-2): Late night/early morning hours increase risk

## 🗂️ Project Structure

```
capstone project/
├── saferouteai/
│   ├── __init__.py
│   ├── config.py              # Configuration
│   ├── orchestrator.py         # Multi-agent orchestrator
│   ├── agents/
│   │   ├── route_analysis_agent.py
│   │   ├── safety_data_agent.py
│   │   ├── risk_scoring_agent.py
│   │   ├── route_optimization_agent.py
│   │   └── alert_agent.py
│   ├── memory/
│   │   ├── __init__.py
│   │   └── session_manager.py  # Session & memory management
│   └── observability/
│       ├── __init__.py
│       ├── logger.py           # Logging setup
│       └── tracer.py           # Operation tracing
├── demo.py                     # Demo script
├── requirements.txt
├── .env.example
└── README.md
```

## 🔍 Evaluation

### Demo Routes

The system includes 5 example routes for evaluation:

1. Downtown to Airport
2. University to Park
3. City Walk
4. Evening Commute
5. Late Night Route

### Evaluation Metrics

- Risk scores for each route
- Safety recommendations
- Alternative route suggestions
- Session statistics (average risk, high-risk routes)
- Operation performance (tracing stats)

## 🎯 Key Capabilities Demonstrated

1. **"Is this route safe right now?"** - Real-time risk assessment
2. **"Recommend a safer alternative."** - Route optimization for high-risk routes
3. **"Alert me if risk changes."** - Session memory tracks route history

## 📝 Submission Components

✅ **Problem Statement**: Real-world safety problem for route planning  
✅ **System Design**: Multi-agent architecture with 5 specialized agents  
✅ **Agent Architecture**: Sequential, parallel, and conditional patterns  
✅ **Tools**: 8+ custom tools for route, weather, safety data  
✅ **Pseudocode**: Clear agent coordination in orchestrator  
✅ **Demo Flow**: Complete demo script with 4 scenarios  
✅ **Evaluation Notes**: Risk scoring, route comparison, statistics  

## 🔧 Configuration

Edit `saferouteai/config.py` to customize:

- Model selection (default: gemini-2.0-flash-exp)
- Risk thresholds (moderate: 4, hazardous: 7)
- API endpoints
- Logging levels

## 📈 Future Enhancements

- Real crime data API integration (police.uk, city datasets)
- Traffic and accident data integration
- Real-time route monitoring and alerts
- Mobile app integration
- Historical route safety trends

## 📄 License

This project is part of a capstone submission demonstrating multi-agent AI systems.

## 🙏 Acknowledgments

- Google AI Agent SDK
- OpenRouteService for routing
- OpenWeather for weather data
- Sunrise-Sunset API for daylight times

---

**Built with Google AI Agent SDK | Multi-Agent System | Real-Time Safety Analysis**

