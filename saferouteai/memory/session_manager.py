"""Session and Memory Management for SafeRouteAI."""
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import saferouteai.config as config


class SessionManager:
    """Manages user sessions and long-term memory."""
    
    def __init__(self, storage_path: str = "./sessions"):
        """
        Initialize session manager.
        
        Args:
            storage_path: Path to store session data
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.sessions: Dict[str, Dict] = {}
        self._load_sessions()
    
    def _load_sessions(self):
        """Load existing sessions from disk."""
        session_files = list(self.storage_path.glob("session_*.json"))
        for session_file in session_files:
            try:
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
                    session_id = session_data.get("session_id")
                    if session_id:
                        self.sessions[session_id] = session_data
            except Exception as e:
                print(f"Error loading session {session_file}: {e}")
    
    def _save_session(self, session_id: str):
        """Save session to disk."""
        if session_id in self.sessions:
            session_file = self.storage_path / f"{session_id}.json"
            try:
                with open(session_file, 'w') as f:
                    json.dump(self.sessions[session_id], f, indent=2, default=str)
            except Exception as e:
                print(f"Error saving session {session_id}: {e}")
    
    def create_session(self, session_id: str) -> Dict[str, Any]:
        """
        Create a new session.
        
        Args:
            session_id: Unique session identifier
        
        Returns:
            Session data
        """
        session_data = {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "route_history": [],
            "user_preferences": {
                "risk_tolerance": "medium",  # low, medium, high
                "preferred_route_type": "driving-car",
                "alert_threshold": 4.0
            },
            "statistics": {
                "total_routes_analyzed": 0,
                "average_risk_score": 0.0,
                "high_risk_routes": 0
            }
        }
        
        self.sessions[session_id] = session_data
        self._save_session(session_id)
        return session_data
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data."""
        return self.sessions.get(session_id)
    
    def store_route_analysis(self, session_id: str, analysis: Dict[str, Any]):
        """
        Store route analysis in session memory.
        
        Args:
            session_id: Session identifier
            analysis: Complete route analysis result
        """
        if session_id not in self.sessions:
            self.create_session(session_id)
        
        session = self.sessions[session_id]
        
        # Add to history
        route_entry = {
            "timestamp": datetime.now().isoformat(),
            "start": analysis.get("summary", {}).get("start"),
            "destination": analysis.get("summary", {}).get("destination"),
            "risk_score": analysis.get("summary", {}).get("risk_score", 0),
            "risk_level": analysis.get("summary", {}).get("risk_level"),
            "distance_km": analysis.get("summary", {}).get("distance_km", 0),
            "duration_minutes": analysis.get("summary", {}).get("duration_minutes", 0)
        }
        
        session["route_history"].append(route_entry)
        
        # Update statistics
        stats = session["statistics"]
        stats["total_routes_analyzed"] += 1
        
        # Update average risk score
        risk_scores = [r["risk_score"] for r in session["route_history"]]
        stats["average_risk_score"] = sum(risk_scores) / len(risk_scores) if risk_scores else 0.0
        
        # Count high risk routes
        stats["high_risk_routes"] = sum(
            1 for r in session["route_history"]
            if r.get("risk_score", 0) >= 7
        )
        
        session["updated_at"] = datetime.now().isoformat()
        self._save_session(session_id)
    
    def get_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get route analysis history for a session."""
        if session_id not in self.sessions:
            return []
        
        return self.sessions[session_id].get("route_history", [])
    
    def get_user_preferences(self, session_id: str) -> Dict[str, Any]:
        """Get user preferences for a session."""
        if session_id not in self.sessions:
            return {}
        
        return self.sessions[session_id].get("user_preferences", {})
    
    def update_user_preferences(
        self,
        session_id: str,
        preferences: Dict[str, Any]
    ):
        """
        Update user preferences.
        
        Args:
            session_id: Session identifier
            preferences: Dictionary of preference updates
        """
        if session_id not in self.sessions:
            self.create_session(session_id)
        
        session = self.sessions[session_id]
        session["user_preferences"].update(preferences)
        session["updated_at"] = datetime.now().isoformat()
        self._save_session(session_id)
    
    def get_statistics(self, session_id: str) -> Dict[str, Any]:
        """Get session statistics."""
        if session_id not in self.sessions:
            return {}
        
        return self.sessions[session_id].get("statistics", {})

