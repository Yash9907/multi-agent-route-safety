# SafeRouteAI - Deployment & Usage Guide

## 📍 Current Usage Methods

### 1. **Local Python Usage** (Current Implementation)

Your project is currently set up for local Python usage:

```python
import asyncio
from saferouteai import SafeRouteOrchestrator

async def main():
    # Create orchestrator
    orchestrator = SafeRouteOrchestrator(session_id="my_session")
    
    # Analyze route
    result = await orchestrator.analyze_route_safety(
        start="37.7749,-122.4194",
        destination="37.6213,-122.3790",
        route_type="driving-car"
    )
    
    print(f"Risk Score: {result['summary']['risk_score']}/10")
    print(result['safety_alert']['alert']['formatted_alert'])

asyncio.run(main())
```

### 2. **Web API Deployment** (Flask/FastAPI)

Create a REST API to use your agent online:

#### Option A: FastAPI (Recommended)

```python
# api_server.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
from saferouteai import SafeRouteOrchestrator

app = FastAPI(title="SafeRouteAI API")

class RouteRequest(BaseModel):
    start: str
    destination: str
    route_type: str = "driving-car"
    session_id: str = None

@app.post("/api/analyze-route")
async def analyze_route(request: RouteRequest):
    try:
        orchestrator = SafeRouteOrchestrator(
            session_id=request.session_id or "default"
        )
        
        result = await orchestrator.analyze_route_safety(
            start=request.start,
            destination=request.destination,
            route_type=request.route_type
        )
        
        return {
            "success": True,
            "risk_score": result['summary']['risk_score'],
            "risk_level": result['summary']['risk_level'],
            "alert": result['safety_alert']['alert']['formatted_alert'],
            "route_info": result['summary']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Run the API:**
```bash
pip install fastapi uvicorn
python api_server.py
```

**Test the API:**
```bash
curl -X POST "http://localhost:8000/api/analyze-route" \
  -H "Content-Type: application/json" \
  -d '{
    "start": "37.7749,-122.4194",
    "destination": "37.6213,-122.3790",
    "route_type": "driving-car"
  }'
```

### 3. **Google AI Studio / Agent Builder Integration**

To use with Google AI Studio's Agent Builder, you need to adapt your agents:

#### Step 1: Create Agent Configuration

```python
# agent_builder_config.py
from google.generativeai import GenerativeModel
import saferouteai.config as config

# Export agent configurations for Google AI Studio
AGENT_CONFIGS = {
    "route_analysis": {
        "model": config.ROUTE_ANALYSIS_MODEL,
        "instructions": """
        You are a Route Analysis Agent. Your role is to:
        1. Analyze routes between start and destination points
        2. Extract route coordinates, distance, and duration
        3. Identify waypoints and route segments
        4. Provide route geometry for safety analysis
        """,
        "tools": ["get_route"]  # Tool names
    },
    "safety_data": {
        "model": config.SAFETY_DATA_MODEL,
        "instructions": """
        You are a Safety Data Agent. Your role is to:
        1. Fetch real-time weather data for route coordinates
        2. Get crime data near route waypoints
        3. Calculate lighting conditions (sunset/sunrise times)
        4. Assess time-of-day safety factors
        """,
        "tools": ["get_weather", "get_lighting_conditions", "get_crime_data", "assess_time_safety"]
    },
    "risk_scoring": {
        "model": config.RISK_SCORING_MODEL,
        "instructions": """
        You are a Risk Scoring Agent. Your role is to:
        1. Analyze aggregated safety data
        2. Compute a combined risk score on a scale of 0-10
        3. Categorize risk levels: Safe (0-3), Moderate (4-6), Hazardous (7-10)
        """,
        "tools": ["calculate_risk_score"]
    }
}
```

#### Step 2: Deploy to Google Cloud Functions

```python
# cloud_function.py
import functions_framework
from saferouteai import SafeRouteOrchestrator
import json

@functions_framework.http
def analyze_route(request):
    """HTTP Cloud Function for route analysis."""
    request_json = request.get_json(silent=True)
    
    if not request_json:
        return {"error": "No JSON payload"}, 400
    
    start = request_json.get('start')
    destination = request_json.get('destination')
    route_type = request_json.get('route_type', 'driving-car')
    
    if not start or not destination:
        return {"error": "Missing start or destination"}, 400
    
    # Run async function
    import asyncio
    orchestrator = SafeRouteOrchestrator()
    result = asyncio.run(
        orchestrator.analyze_route_safety(start, destination, route_type)
    )
    
    return {
        "risk_score": result['summary']['risk_score'],
        "risk_level": result['summary']['risk_level'],
        "alert": result['safety_alert']['alert']['formatted_alert']
    }
```

**Deploy to Cloud Functions:**
```bash
gcloud functions deploy analyze_route \
  --runtime python311 \
  --trigger-http \
  --allow-unauthenticated \
  --source .
```

### 4. **Package Installation** (Use as Library)

Make your project installable as a package:

```python
# setup.py
from setuptools import setup, find_packages

setup(
    name="saferouteai",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "google-generativeai>=0.3.0",
        "python-dotenv>=1.0.0",
        "openrouteservice>=2.3.0",
        "geopy>=2.4.0",
        "requests>=2.31.0",
    ],
    entry_points={
        "console_scripts": [
            "saferouteai=demo:main",
        ],
    },
)
```

**Install and use:**
```bash
pip install -e .
python -m saferouteai
```

### 5. **Streamlit Web Interface** (User-Friendly UI)

Create a web interface:

```python
# streamlit_app.py
import streamlit as st
import asyncio
from saferouteai import SafeRouteOrchestrator

st.title("🚦 SafeRouteAI - Route Safety Advisor")

# Input form
col1, col2 = st.columns(2)
with col1:
    start = st.text_input("Start Location (lat,lon)", "37.7749,-122.4194")
with col2:
    destination = st.text_input("Destination (lat,lon)", "37.6213,-122.3790")

route_type = st.selectbox("Route Type", ["driving-car", "foot-walking", "cycling-regular"])

if st.button("Analyze Route Safety"):
    with st.spinner("Analyzing route..."):
        orchestrator = SafeRouteOrchestrator()
        result = asyncio.run(
            orchestrator.analyze_route_safety(start, destination, route_type)
        )
        
        # Display results
        st.success(f"Risk Score: {result['summary']['risk_score']}/10")
        st.info(f"Risk Level: {result['summary']['risk_level']}")
        st.text_area("Safety Alert", result['safety_alert']['alert']['formatted_alert'])
```

**Run Streamlit:**
```bash
pip install streamlit
streamlit run streamlit_app.py
```

### 6. **Docker Deployment**

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["python", "api_server.py"]
```

**Build and run:**
```bash
docker build -t saferouteai .
docker run -p 8000:8000 --env-file .env saferouteai
```

## 🔗 Integration Options

### Google AI Studio
- Use Agent Builder UI to create agents
- Import your tool definitions
- Deploy as webhook or Cloud Function

### Google Cloud Run
- Deploy FastAPI app to Cloud Run
- Auto-scaling, HTTPS included
- Pay per use

### Heroku / Railway
- Simple deployment platforms
- Connect GitHub repo
- Auto-deploy on push

### Local Network
- Run FastAPI server
- Access from other devices on network
- Use for internal tools

## 📝 Environment Variables

Make sure to set these in your deployment:

```bash
GOOGLE_API_KEY=your_key
ORS_API_KEY=your_key
OPENWEATHER_API_KEY=your_key
```

## 🚀 Quick Start Commands

```bash
# Local usage
python demo.py

# Web API
python api_server.py

# Streamlit UI
streamlit run streamlit_app.py

# Docker
docker-compose up
```

