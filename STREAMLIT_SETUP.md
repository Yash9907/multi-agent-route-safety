# Streamlit Setup Guide

## Quick Install (Try This First)

```bash
pip install streamlit
```

If this fails with cmake errors, follow the steps below.

## Full Installation Steps for Windows

### Step 1: Install Visual Studio Build Tools

1. Download Visual Studio Build Tools:
   - Go to: https://visualstudio.microsoft.com/downloads/
   - Scroll down to "All downloads" → "Tools for Visual Studio"
   - Download "Build Tools for Visual Studio 2022"

2. Run the installer and select:
   - ✅ **Desktop development with C++** workload
   - This includes MSVC compiler, Windows SDK, and CMake

3. Click "Install" (takes ~3-5 GB, 10-20 minutes)

### Step 2: Install CMake (if not included)

1. Download CMake: https://cmake.org/download/
2. Choose "Windows x64 Installer"
3. During installation, select "Add CMake to system PATH"
4. Restart your terminal/PowerShell

### Step 3: Install Streamlit

```bash
# Restart terminal after installing build tools
pip install streamlit
```

### Step 4: Run Your App

```bash
streamlit run streamlit_app.py
```

The app will open automatically in your browser at `http://localhost:8501`

## Alternative: Use Python 3.11 or 3.12

These versions have pre-built wheels, so no build tools needed:

1. Install Python 3.11 or 3.12 from python.org
2. Create new virtual environment:
   ```bash
   py -3.11 -m venv venv_streamlit
   venv_streamlit\Scripts\activate
   pip install -r requirements.txt
   pip install streamlit
   streamlit run streamlit_app.py
   ```

## Quick Test

After installation, verify it works:

```bash
streamlit --version
# Should show: Streamlit, version 1.x.x
```

## Troubleshooting

### Error: "cmake not found"
- Make sure CMake is installed and in PATH
- Restart terminal after installation

### Error: "Microsoft Visual C++ 14.0 or greater is required"
- Install Visual Studio Build Tools with C++ workload
- Restart terminal

### Still having issues?
Use the API server instead - it works immediately:
```bash
python api_server.py
# Visit http://localhost:8000/docs
```

## What Your Streamlit App Includes

✅ **Single Route Analysis** - Analyze one route at a time
✅ **Batch Analysis** - Analyze multiple routes in parallel
✅ **Session History** - View past route analyses
✅ **Risk Breakdown** - See weather, crime, lighting, time risks
✅ **Safety Alerts** - Get formatted safety recommendations

