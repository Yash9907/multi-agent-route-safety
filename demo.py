"""
SafeRouteAI Demo Script
Demonstrates the multi-agent route safety analysis system.
"""
import asyncio
import json
from datetime import datetime
from saferouteai import SafeRouteOrchestrator
from saferouteai.observability.logger import setup_logger

# Setup logger
logger = setup_logger("SafeRouteDemo")

# Example routes for demonstration
DEMO_ROUTES = [
    {
        "name": "Downtown to Airport",
        "start": "37.7749,-122.4194",  # San Francisco downtown
        "destination": "37.6213,-122.3790",  # SFO Airport
        "route_type": "driving-car"
    },
    {
        "name": "University to Park",
        "start": "37.8715,-122.2730",  # UC Berkeley
        "destination": "37.8044,-122.2712",  # Tilden Park
        "route_type": "driving-car"
    },
    {
        "name": "City Walk",
        "start": "37.7849,-122.4094",  # SF Financial District
        "destination": "37.8024,-122.4058",  # Fisherman's Wharf
        "route_type": "foot-walking"
    },
    {
        "name": "Evening Commute",
        "start": "37.7849,-122.4094",  # SF Financial District
        "destination": "37.7849,-122.4094",  # Same location (for testing)
        "route_type": "driving-car"
    },
    {
        "name": "Late Night Route",
        "start": "37.7749,-122.4194",  # SF Downtown
        "destination": "37.7849,-122.4094",  # SF Financial District
        "route_type": "foot-walking"
    }
]


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_route_analysis(result: dict):
    """Print formatted route analysis results."""
    if not result.get("success"):
        print(f"❌ Error: {result.get('error', 'Unknown error')}")
        return
    
    summary = result.get("summary", {})
    risk_assessment = result.get("risk_assessment", {})
    alert = result.get("safety_alert", {})
    
    print(f"\n📍 Route: {summary.get('start')} → {summary.get('destination')}")
    print(f"   Distance: {summary.get('distance_km', 0):.2f} km")
    print(f"   Duration: {summary.get('duration_minutes', 0):.2f} minutes")
    print(f"   Route Type: {summary.get('route_type', 'Unknown')}")
    
    print(f"\n⚠️  Risk Assessment:")
    print(f"   Risk Score: {summary.get('risk_score', 0):.2f}/10")
    print(f"   Risk Level: {summary.get('risk_level', 'Unknown')}")
    
    # Risk breakdown
    risk_breakdown = risk_assessment.get("risk_breakdown", {})
    if risk_breakdown:
        print(f"\n   Risk Breakdown:")
        for factor, score in risk_breakdown.items():
            print(f"     - {factor.capitalize()}: {score:.2f}")
    
    # Primary risks
    primary_risks = risk_assessment.get("primary_risks", [])
    if primary_risks:
        print(f"\n   Primary Concerns:")
        for risk in primary_risks:
            print(f"     - {risk['factor'].capitalize()}: {risk['score']:.2f}")
    
    # Safety alert
    if alert:
        formatted_alert = alert.get("alert", {})
        if formatted_alert.get("formatted_alert"):
            print(f"\n📢 Safety Alert:")
            print(formatted_alert["formatted_alert"])
    
    # Optimization recommendation
    optimization = result.get("route_optimization")
    if optimization and optimization.get("optimization_needed"):
        print(f"\n🔄 Route Optimization:")
        if optimization.get("should_use_alternative"):
            print("   ✅ Alternative route recommended!")
            comparison = optimization.get("comparison", {})
            comp_data = comparison.get("comparison", {})
            print(f"   Risk Improvement: {optimization.get('risk_improvement', 0):.2f} points")
            print(f"   Distance Change: {comp_data.get('distance', {}).get('difference_km', 0):.2f} km")
            print(f"   Time Change: {comp_data.get('time', {}).get('difference_minutes', 0):.2f} minutes")
        else:
            print("   ℹ️  Alternative route available but not significantly safer")
    
    print("\n" + "-" * 80)


async def demo_single_route():
    """Demonstrate single route analysis."""
    print_section("Demo 1: Single Route Analysis")
    
    orchestrator = SafeRouteOrchestrator(session_id="demo_session_1")
    
    route = DEMO_ROUTES[0]
    print(f"Analyzing route: {route['name']}")
    print(f"Start: {route['start']}")
    print(f"Destination: {route['destination']}")
    
    result = await orchestrator.analyze_route_safety(
        start=route["start"],
        destination=route["destination"],
        route_type=route["route_type"]
    )
    
    print_route_analysis(result)
    
    # Show session history
    history = orchestrator.get_session_history()
    if history:
        print(f"\n📊 Session History: {len(history)} routes analyzed")
        for i, entry in enumerate(history[-3:], 1):  # Show last 3
            print(f"   {i}. Risk: {entry.get('risk_score', 0):.2f} - {entry.get('start')} → {entry.get('destination')}")


async def demo_batch_analysis():
    """Demonstrate batch route analysis (parallel agents)."""
    print_section("Demo 2: Batch Route Analysis (Parallel Agents)")
    
    orchestrator = SafeRouteOrchestrator(session_id="demo_session_2")
    
    routes = DEMO_ROUTES[:3]  # Analyze first 3 routes
    print(f"Analyzing {len(routes)} routes in parallel...\n")
    
    results = await orchestrator.batch_analyze_routes(
        routes=[{"start": r["start"], "destination": r["destination"]} for r in routes],
        route_type="driving-car"
    )
    
    print(f"\n✅ Completed analysis of {len(results)} routes\n")
    
    for i, (route, result) in enumerate(zip(routes, results), 1):
        print(f"\n{'='*80}")
        print(f"Route {i}: {route['name']}")
        print_route_analysis(result)
    
    # Show statistics
    stats = orchestrator.session_manager.get_statistics(orchestrator.session_id) if orchestrator.session_manager else {}
    if stats:
        print(f"\n📊 Batch Analysis Statistics:")
        print(f"   Total Routes: {stats.get('total_routes_analyzed', 0)}")
        print(f"   Average Risk Score: {stats.get('average_risk_score', 0):.2f}")
        print(f"   High Risk Routes: {stats.get('high_risk_routes', 0)}")


async def demo_memory_and_preferences():
    """Demonstrate memory and user preferences."""
    print_section("Demo 3: Memory & User Preferences")
    
    orchestrator = SafeRouteOrchestrator(session_id="demo_session_3")
    
    # Set user preferences
    print("Setting user preferences...")
    orchestrator.update_user_preferences({
        "risk_tolerance": "low",
        "alert_threshold": 3.0,
        "preferred_route_type": "driving-car"
    })
    
    preferences = orchestrator.get_user_preferences()
    print(f"\n✅ User Preferences:")
    for key, value in preferences.items():
        print(f"   {key}: {value}")
    
    # Analyze a route
    route = DEMO_ROUTES[1]
    print(f"\nAnalyzing route with user preferences...")
    result = await orchestrator.analyze_route_safety(
        start=route["start"],
        destination=route["destination"],
        route_type=route["route_type"]
    )
    
    print_route_analysis(result)
    
    # Show full history
    history = orchestrator.get_session_history()
    print(f"\n📚 Full Session History ({len(history)} routes):")
    for i, entry in enumerate(history, 1):
        print(f"   {i}. [{entry.get('timestamp', 'Unknown')}] "
              f"Risk: {entry.get('risk_score', 0):.2f} - "
              f"{entry.get('start')} → {entry.get('destination')}")


async def demo_observability():
    """Demonstrate observability features."""
    print_section("Demo 4: Observability (Logging & Tracing)")
    
    orchestrator = SafeRouteOrchestrator(session_id="demo_session_4")
    
    route = DEMO_ROUTES[2]
    print(f"Analyzing route with full observability...")
    print("(Check logs/ directory for detailed logs)\n")
    
    result = await orchestrator.analyze_route_safety(
        start=route["start"],
        destination=route["destination"],
        route_type=route["route_type"]
    )
    
    print_route_analysis(result)
    
    # Show trace statistics
    stats = orchestrator.tracer.get_operation_stats()
    if stats:
        print(f"\n📈 Operation Statistics:")
        for op_name, op_stats in stats.items():
            print(f"\n   {op_name}:")
            print(f"     Count: {op_stats['count']}")
            print(f"     Avg Duration: {op_stats['avg_duration']:.4f}s")
            print(f"     Min Duration: {op_stats['min_duration']:.4f}s")
            print(f"     Max Duration: {op_stats['max_duration']:.4f}s")


async def main():
    """Run all demos."""
    print("\n" + "=" * 80)
    print("  SafeRouteAI - Real-Time Route Safety Advisor")
    print("  Multi-Agent System Demo")
    print("=" * 80)
    
    try:
        # Demo 1: Single route analysis
        await demo_single_route()
        
        # Demo 2: Batch analysis (parallel agents)
        await demo_batch_analysis()
        
        # Demo 3: Memory and preferences
        await demo_memory_and_preferences()
        
        # Demo 4: Observability
        await demo_observability()
        
        print_section("Demo Complete")
        print("\n✅ All demos completed successfully!")
        print("\nKey Features Demonstrated:")
        print("  ✓ Multi-agent system (5 specialized agents)")
        print("  ✓ Sequential agent coordination")
        print("  ✓ Parallel batch processing")
        print("  ✓ Session & memory management")
        print("  ✓ Observability (logging & tracing)")
        print("  ✓ Custom tools (route APIs, weather, lighting)")
        print("  ✓ Risk scoring and route optimization")
        print("\nCheck the 'logs/' directory for detailed operation logs.")
        print("Check the 'sessions/' directory for stored session data.")
        
    except Exception as e:
        logger.error(f"Demo error: {str(e)}", exc_info=True)
        print(f"\n❌ Error during demo: {str(e)}")
        print("Check logs for details.")


if __name__ == "__main__":
    asyncio.run(main())

