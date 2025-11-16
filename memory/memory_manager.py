"""Memory management system for EduMentor agents."""
from typing import Dict, List, Any, Optional
from google.ai import agent
import json
import os
from datetime import datetime
from pathlib import Path


class InMemorySessionService:
    """In-memory session service for managing agent sessions."""
    
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
    
    def create_session(self, session_id: str, user_id: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Create a new session."""
        session = {
            "session_id": session_id,
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "metadata": metadata or {},
            "conversation_history": [],
            "context": {}
        }
        self.sessions[session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID."""
        return self.sessions.get(session_id)
    
    def update_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Update session data."""
        if session_id not in self.sessions:
            return False
        self.sessions[session_id].update(updates)
        self.sessions[session_id]["updated_at"] = datetime.now().isoformat()
        return True
    
    def add_to_history(self, session_id: str, role: str, content: str) -> bool:
        """Add message to conversation history."""
        if session_id not in self.sessions:
            return False
        self.sessions[session_id]["conversation_history"].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        return True
    
    def get_history(self, session_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get conversation history."""
        if session_id not in self.sessions:
            return []
        history = self.sessions[session_id]["conversation_history"]
        if limit:
            return history[-limit:]
        return history


class MemoryBank:
    """Long-term memory bank for storing user preferences and performance."""
    
    def __init__(self, storage_path: str = "./memory_bank"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.memory_file = self.storage_path / "memory.json"
        self.memory: Dict[str, Any] = self._load_memory()
    
    def _load_memory(self) -> Dict[str, Any]:
        """Load memory from disk."""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {"users": {}, "topics": {}, "performance": {}}
        return {"users": {}, "topics": {}, "performance": {}}
    
    def _save_memory(self):
        """Save memory to disk."""
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, indent=2, ensure_ascii=False)
    
    def store_user_preference(self, user_id: str, key: str, value: Any):
        """Store user preference."""
        if user_id not in self.memory["users"]:
            self.memory["users"][user_id] = {"preferences": {}, "history": []}
        self.memory["users"][user_id]["preferences"][key] = value
        self._save_memory()
    
    def get_user_preference(self, user_id: str, key: str, default: Any = None) -> Any:
        """Get user preference."""
        if user_id not in self.memory["users"]:
            return default
        return self.memory["users"][user_id]["preferences"].get(key, default)
    
    def record_performance(self, user_id: str, topic: str, score: float, quiz_id: str):
        """Record user performance on quizzes."""
        if user_id not in self.memory["performance"]:
            self.memory["performance"][user_id] = []
        
        record = {
            "topic": topic,
            "score": score,
            "quiz_id": quiz_id,
            "timestamp": datetime.now().isoformat()
        }
        self.memory["performance"][user_id].append(record)
        self._save_memory()
    
    def get_performance_history(self, user_id: str, topic: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get performance history for user."""
        if user_id not in self.memory["performance"]:
            return []
        
        history = self.memory["performance"][user_id]
        if topic:
            return [h for h in history if h["topic"] == topic]
        return history
    
    def get_average_score(self, user_id: str, topic: Optional[str] = None) -> float:
        """Get average score for user."""
        history = self.get_performance_history(user_id, topic)
        if not history:
            return 0.0
        return sum(h["score"] for h in history) / len(history)
    
    def store_topic_knowledge(self, topic: str, knowledge: Dict[str, Any]):
        """Store knowledge about a topic."""
        if topic not in self.memory["topics"]:
            self.memory["topics"][topic] = {}
        self.memory["topics"][topic].update(knowledge)
        self.memory["topics"][topic]["last_updated"] = datetime.now().isoformat()
        self._save_memory()
    
    def get_topic_knowledge(self, topic: str) -> Dict[str, Any]:
        """Get stored knowledge about a topic."""
        return self.memory["topics"].get(topic, {})


class ContextCompactor:
    """Context compaction utility for managing conversation context."""
    
    @staticmethod
    def compact_context(history: List[Dict[str, Any]], max_tokens: int = 2000) -> List[Dict[str, Any]]:
        """
        Compact conversation history to fit within token limit.
        Keeps most recent messages and summarizes older ones.
        """
        if len(history) <= 10:  # Keep all if small
            return history
        
        # Keep most recent 5 messages
        recent = history[-5:]
        
        # Summarize older messages
        older = history[:-5]
        summary = {
            "role": "system",
            "content": f"Previous conversation summary: {len(older)} messages about various topics.",
            "timestamp": older[0]["timestamp"] if older else datetime.now().isoformat()
        }
        
        return [summary] + recent



