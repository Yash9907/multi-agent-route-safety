# SafeRouteAI - Usage Guide

## 🚀 Quick Start Options

### Option 1: Use the API Server (Recommended - No Streamlit needed)

The API server doesn't require Streamlit and works immediately:

```bash
# Install core dependencies (no Streamlit)
pip install fastapi uvicorn google-generativeai python-dotenv pydantic requests openrouteservice geopy pandas numpy

# Run the API server
python api_server.py
```

Then access:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

**Test the API:**
```bash
curl -X POST "http://localhost:8000/api/analyze-route" \
  -H "Content-Type: application/json" \
  -d '{"start": "37.7749,-122.4194", "destination": "37.6213,-122.3790"}'
```

### Option 2: Use Python Directly (Simplest)

```python
import asyncio
from saferouteai import SafeRouteOrchestrator

async def main():
    orchestrator = SafeRouteOrchestrator(session_id="my_session")
    
    result = await orchestrator.analyze_route_safety(
        start="37.7749,-122.4194",
        destination="37.6213,-122.3790",
        route_type="driving-car"
    )
    
    print(f"Risk Score: {result['summary']['risk_score']}/10")
    print(result['safety_alert']['alert']['formatted_alert'])

asyncio.run(main())
```

### Option 3: Streamlit Web UI (Optional - Requires cmake)

If you want the web UI, you need to install build tools first:

**Windows:**
1. Install Visual Studio Build Tools: https://visualstudio.microsoft.com/downloads/
   - Select "Desktop development with C++"
2. Install CMake: https://cmake.org/download/
3. Then install Streamlit:
```bash
pip install streamlit
streamlit run streamlit_app.py
```

**Alternative (Easier):** Use the API server instead - it provides the same functionality via HTTP!

## 📡 Using the API Server

### Start the Server

```bash
python api_server.py
```

### API Endpoints

#### 1. Analyze Single Route
```bash
POST /api/analyze-route
Content-Type: application/json

{
  "start": "37.7749,-122.4194",
  "destination": "37.6213,-122.3790",
  "route_type": "driving-car",
  "session_id": "optional_session_id"
}
```

#### 2. Batch Analyze Routes
```bash
POST /api/batch-analyze
Content-Type: application/json

{
  "routes": [
    {"start": "37.7749,-122.4194", "destination": "37.6213,-122.3790"},
    {"start": "37.8715,-122.2730", "destination": "37.8044,-122.2712"}
  ],
  "route_type": "driving-car"
}
```

#### 3. Get Session History
```bash
GET /api/session/{session_id}/history
```

### Using from Python

```python
import requests

# Analyze a route
response = requests.post(
    "http://localhost:8000/api/analyze-route",
    json={
        "start": "37.7749,-122.4194",
        "destination": "37.6213,-122.3790",
        "route_type": "driving-car"
    }
)

result = response.json()
print(f"Risk Score: {result['risk_score']}/10")
print(result['alert'])
```

### Using from JavaScript/Web

```javascript
fetch('http://localhost:8000/api/analyze-route', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    start: "37.7749,-122.4194",
    destination: "37.6213,-122.3790",
    route_type: "driving-car"
  })
})
.then(res => res.json())
.then(data => console.log(data));
```

## 🌐 Deploy Online

### Deploy to Google Cloud Run

```bash
# Install gcloud CLI
# Create Dockerfile (see DEPLOYMENT.md)

gcloud run deploy saferouteai-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Deploy to Heroku

```bash
heroku create saferouteai-api
git push heroku main
```

### Deploy to Railway

1. Connect GitHub repo
2. Railway auto-detects and deploys
3. Set environment variables in dashboard

## 📝 Environment Variables

Create a `.env` file:

```bash
GOOGLE_API_KEY=your_google_api_key
ORS_API_KEY=your_ors_api_key
OPENWEATHER_API_KEY=your_openweather_api_key
```

## ✅ Recommended Setup

For the easiest setup, use the **API Server**:

1. Install dependencies (without Streamlit):
```bash
pip install -r requirements.txt
```

2. Run the API:
```bash
python api_server.py
```

3. Access at http://localhost:8000/docs

This gives you:
- ✅ REST API for integration
- ✅ Interactive API documentation
- ✅ No build tools needed
- ✅ Works on any platform
- ✅ Can be deployed anywhere

