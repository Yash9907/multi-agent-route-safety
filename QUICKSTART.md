# SafeRouteAI Quick Start Guide

## 🚀 Quick Setup (5 minutes)

### Step 1:  
```bash
pip install -r requirements.txt
```

### Step 2: Get API Keys (All Free)

1. **Google AI API Key**
   - Visit: https://aistudio.google.com/apikey
   - Create a new API key
   - Copy the key

2. **OpenRouteService API Key**
   - Visit: https://openrouteservice.org/dev/#/signup
   - Sign up for free account
   - Get your API key from dashboard

3. **OpenWeather API Key**
   - Visit: https://openweathermap.org/api
   - Sign up for free account
   - Get your API key

### Step 3: Configure Environment

Create a `.env` file in the project root:

```bash
GOOGLE_API_KEY=your_google_api_key_here
ORS_API_KEY=your_ors_api_key_here
OPENWEATHER_API_KEY=your_openweather_api_key_here
```

### Step 4: Run Demo

```bash
python demo.py
```

This will run 4 demo scenarios:
1. Single route analysis
2. Batch route analysis (parallel)
3. Memory & preferences
4. Observability

## 📝 Example Usage

### Basic Route Analysis

```python
import asyncio
from saferouteai import SafeRouteOrchestrator

async def main():
    # Create orchestrator
    orchestrator = SafeRouteOrchestrator(session_id="my_session")
    
    # Analyze a route
    result = await orchestrator.analyze_route_safety(
        start="37.7749,-122.4194",      # San Francisco
        destination="37.6213,-122.3790", # SFO Airport
        route_type="driving-car"
    )
    
    # Print results
    print(f"Risk Score: {result['summary']['risk_score']}/10")
    print(f"Risk Level: {result['summary']['risk_level']}")
    
    # Get safety alert
    alert = result['safety_alert']['alert']['formatted_alert']
    print(alert)

asyncio.run(main())
```

### Batch Analysis (Parallel Agents)

```python
routes = [
    {"start": "37.7749,-122.4194", "destination": "37.6213,-122.3790"},
    {"start": "37.8715,-122.2730", "destination": "37.8044,-122.2712"},
]

results = await orchestrator.batch_analyze_routes(routes)
```

### With User Preferences

```python
orchestrator.update_user_preferences({
    "risk_tolerance": "low",
    "alert_threshold": 3.0
})

result = await orchestrator.analyze_route_safety(...)
```

## 🧪 Testing Without API Keys

The system includes fallback mechanisms:
- Route analysis: Uses straight-line distance if ORS key missing
- Weather: Returns moderate risk if OpenWeather key missing
- Crime data: Uses fallback assessment

**Note**: For full functionality, all API keys are recommended.

## 📊 Understanding Results

### Risk Scores
- **0-3**: Safe ✅
- **4-6**: Moderate ⚡
- **7-10**: Hazardous ⚠️

### Output Structure
```python
{
    "success": True,
    "summary": {
        "risk_score": 5.2,
        "risk_level": "Moderate",
        "distance_km": 12.5,
        "duration_minutes": 18.3
    },
    "risk_assessment": {
        "risk_breakdown": {...},
        "primary_risks": [...]
    },
    "safety_alert": {
        "alert": {
            "formatted_alert": "..."
        }
    },
    "route_optimization": {...}  # Only if risk >= 4
}
```

## 🔍 Troubleshooting

### Import Errors
```bash
# Make sure you're in the project root
cd "capstone project"
python demo.py
```

### API Key Errors
- Check `.env` file exists and has correct keys
- Verify API keys are valid
- Check API quotas (free tiers have limits)

### Route Analysis Fails
- Verify coordinates are in "lat,lon" format
- Check internet connection
- Review logs in `logs/` directory

## 📁 Project Structure

```
saferouteai/
├── agents/          # 5 specialized agents
├── memory/            # Session management
├── observability/     # Logging & tracing
└── orchestrator.py   # Multi-agent coordinator

demo.py                # Demo script
logs/                  # Generated logs
sessions/              # Session data
```

## 🎯 Next Steps

1. Run `demo.py` to see all features
2. Check `logs/` for detailed operation logs
3. Review `sessions/` for stored route history
4. Customize `saferouteai/config.py` for your needs

## 💡 Tips

- Use session IDs to track multiple users
- Enable memory to build route history
- Check trace statistics for performance insights
- Customize risk thresholds in config.py

---

**Ready to analyze routes safely! 🛣️**

