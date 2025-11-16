"""
SafeRouteAI Streamlit Web Interface
Run: streamlit run streamlit_app.py
"""
import streamlit as st
import asyncio
from saferouteai import SafeRouteOrchestrator
from datetime import datetime

st.set_page_config(
    page_title="SafeRouteAI - Route Safety Advisor",
    page_icon="🚦",
    layout="wide"
)

st.title("🚦 SafeRouteAI")
st.subheader("Real-Time Route Safety Advisor - Multi-Agent System")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    session_id = st.text_input("Session ID", value=f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    route_type = st.selectbox(
        "Route Type",
        ["driving-car", "foot-walking", "cycling-regular"],
        index=0
    )
    
    st.header("📊 About")
    st.info("""
    SafeRouteAI analyzes route safety by considering:
    - Weather conditions
    - Crime data
    - Lighting conditions
    - Time of day
    
    Risk scores: 0-3 (Safe), 4-6 (Moderate), 7-10 (Hazardous)
    """)

# Main interface
tab1, tab2, tab3 = st.tabs(["📍 Single Route", "📋 Batch Analysis", "📚 Session History"])

with tab1:
    st.header("Analyze Single Route")
    
    col1, col2 = st.columns(2)
    with col1:
        start = st.text_input(
            "Start Location (lat,lon)",
            value="37.7749,-122.4194",
            help="Enter coordinates as latitude,longitude"
        )
    with col2:
        destination = st.text_input(
            "Destination (lat,lon)",
            value="37.6213,-122.3790",
            help="Enter coordinates as latitude,longitude"
        )
    
    if st.button("🔍 Analyze Route Safety", type="primary"):
        if not start or not destination:
            st.error("Please enter both start and destination locations")
        else:
            with st.spinner("Analyzing route with multi-agent system..."):
                try:
                    orchestrator = SafeRouteOrchestrator(session_id=session_id)
                    result = asyncio.run(
                        orchestrator.analyze_route_safety(
                            start=start,
                            destination=destination,
                            route_type=route_type
                        )
                    )
                    
                    if result.get("success", False):
                        # Display results
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            risk_score = result['summary']['risk_score']
                            if risk_score <= 3:
                                st.metric("Risk Score", f"{risk_score}/10", "✅ Safe")
                            elif risk_score <= 6:
                                st.metric("Risk Score", f"{risk_score}/10", "⚠️ Moderate")
                            else:
                                st.metric("Risk Score", f"{risk_score}/10", "🚨 Hazardous")
                        
                        with col2:
                            st.metric("Distance", f"{result['summary'].get('distance_km', 0):.2f} km")
                        
                        with col3:
                            st.metric("Duration", f"{result['summary'].get('duration_minutes', 0):.1f} min")
                        
                        # Risk breakdown
                        st.subheader("📊 Risk Breakdown")
                        risk_breakdown = result['risk_assessment'].get('risk_breakdown', {})
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Weather", f"{risk_breakdown.get('weather', 0):.1f}")
                        with col2:
                            st.metric("Crime", f"{risk_breakdown.get('crime', 0):.1f}")
                        with col3:
                            st.metric("Lighting", f"{risk_breakdown.get('lighting', 0):.1f}")
                        with col4:
                            st.metric("Time", f"{risk_breakdown.get('time', 0):.1f}")
                        
                        # Safety alert
                        st.subheader("📢 Safety Alert")
                        alert_text = result['safety_alert']['alert']['formatted_alert']
                        st.text_area("", alert_text, height=200, disabled=True)
                        
                        # Optimization
                        if result['summary'].get('optimization_recommended', False):
                            st.warning("🔄 Alternative route available! Check optimization details.")
                    else:
                        st.error(f"Analysis failed: {result.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    st.error(f"Error: {str(e)}")

with tab2:
    st.header("Batch Route Analysis")
    st.info("Analyze multiple routes in parallel using parallel agents")
    
    # Example routes
    example_routes = [
        {"start": "37.7749,-122.4194", "destination": "37.6213,-122.3790"},
        {"start": "37.8715,-122.2730", "destination": "37.8044,-122.2712"},
        {"start": "37.7849,-122.4094", "destination": "37.8024,-122.4058"}
    ]
    
    routes_text = st.text_area(
        "Routes (JSON format)",
        value=str(example_routes),
        height=150,
        help="List of routes: [{'start': 'lat,lon', 'destination': 'lat,lon'}, ...]"
    )
    
    if st.button("🔍 Analyze All Routes", type="primary"):
        try:
            import json
            routes = json.loads(routes_text)
            
            with st.spinner(f"Analyzing {len(routes)} routes in parallel..."):
                orchestrator = SafeRouteOrchestrator(session_id=session_id)
                results = asyncio.run(
                    orchestrator.batch_analyze_routes(routes, route_type=route_type)
                )
                
                # Display results
                st.subheader(f"📊 Results: {len(results)} routes analyzed")
                for i, result in enumerate(results):
                    with st.expander(f"Route {i+1}: {result['summary'].get('start', 'N/A')} → {result['summary'].get('destination', 'N/A')}"):
                        if result.get("success", False):
                            st.metric("Risk Score", f"{result['summary']['risk_score']}/10")
                            st.write(f"**Risk Level:** {result['summary']['risk_level']}")
                            st.write(f"**Distance:** {result['summary'].get('distance_km', 0):.2f} km")
                        else:
                            st.error(f"Error: {result.get('error', 'Unknown')}")
        except Exception as e:
            st.error(f"Error parsing routes: {str(e)}")

with tab3:
    st.header("Session History")
    st.info(f"View route analysis history for session: {session_id}")
    
    if st.button("📚 Load History"):
        try:
            orchestrator = SafeRouteOrchestrator(session_id=session_id)
            history = orchestrator.get_session_history()
            
            if history:
                st.subheader(f"📋 {len(history)} routes analyzed")
                for i, entry in enumerate(history):
                    with st.expander(f"Route {i+1}: {entry.get('start', 'N/A')} → {entry.get('destination', 'N/A')}"):
                        st.write(f"**Risk Score:** {entry.get('risk_score', 0):.2f}/10")
                        st.write(f"**Timestamp:** {entry.get('timestamp', 'N/A')}")
            else:
                st.info("No history found for this session")
        except Exception as e:
            st.error(f"Error loading history: {str(e)}")

