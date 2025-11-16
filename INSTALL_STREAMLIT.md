# Installing Streamlit for SafeRouteAI

## The Issue
Streamlit requires `pyarrow` which needs C++ build tools on Windows. Python 3.14 might not have pre-built wheels yet.

## Solution Options

### Option 1: Install Build Tools (Recommended for Windows)

1. **Install Visual Studio Build Tools:**
   - Download: https://visualstudio.microsoft.com/downloads/
   - Run installer
   - Select "Desktop development with C++" workload
   - Install (takes ~3-5 GB)

2. **Install CMake:**
   - Download: https://cmake.org/download/
   - Install and add to PATH

3. **Then install Streamlit:**
   ```bash
   pip install streamlit
   ```

### Option 2: Use Python 3.11 or 3.12 (Easier)

Python 3.11/3.12 have pre-built wheels for pyarrow, so no build tools needed:

1. Install Python 3.11 or 3.12
2. Create new virtual environment:
   ```bash
   python3.11 -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   pip install streamlit
   ```

### Option 3: Try Installing Pre-built Wheel

Sometimes pip can find a compatible wheel:

```bash
pip install streamlit --upgrade
```

### Option 4: Use Streamlit Cloud (No Installation Needed)

Deploy to Streamlit Cloud for free:
1. Push code to GitHub
2. Go to https://share.streamlit.io
3. Connect repository
4. Deploy automatically

## Quick Test

After installation, test Streamlit:

```bash
streamlit --version
```

Then run your app:

```bash
streamlit run streamlit_app.py
```

## Alternative: Use API Server Instead

If Streamlit installation is too complex, the API server works immediately:

```bash
python api_server.py
# Visit http://localhost:8000/docs
```

This provides the same functionality without build tools!

