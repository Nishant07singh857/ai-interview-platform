"""
WebSocket Manager - Manage WebSocket connections for real-time interviews
"""

from typing import Dict, Set
from fastapi import WebSocket
import logging
import json

logger = logging.getLogger(__name__)

class WebSocketManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.user_sessions: Dict[str, str] = {}  # user_id -> session_id
    
    async def connect(self, websocket: WebSocket, session_id: str):
        """Accept WebSocket connection"""
        await websocket.accept()
        
        if session_id not in self.active_connections:
            self.active_connections[session_id] = set()
        
        self.active_connections[session_id].add(websocket)
        logger.info(f"WebSocket connected for session {session_id}")
    
    def disconnect(self, websocket: WebSocket, session_id: str):
        """Disconnect WebSocket"""
        if session_id in self.active_connections:
            self.active_connections[session_id].discard(websocket)
            
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
        
        logger.info(f"WebSocket disconnected from session {session_id}")
    
    async def send_message(self, session_id: str, message: Dict):
        """Send message to all connections in a session"""
        if session_id in self.active_connections:
            for connection in self.active_connections[session_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending message: {str(e)}")
    
    async def send_personal_message(self, user_id: str, message: Dict):
        """Send message to a specific user"""
        if user_id in self.user_sessions:
            session_id = self.user_sessions[user_id]
            await self.send_message(session_id, message)
    
    def register_user(self, user_id: str, session_id: str):
        """Register user with session"""
        self.user_sessions[user_id] = session_id
    
    def unregister_user(self, user_id: str):
        """Unregister user"""
        if user_id in self.user_sessions:
            del self.user_sessions[user_id]
    
    async def broadcast(self, message: Dict):
        """Broadcast message to all connected clients"""
        for session_id, connections in self.active_connections.items():
            for connection in connections:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting message: {str(e)}")
    
    def get_connection_count(self) -> int:
        """Get total number of active connections"""
        count = 0
        for connections in self.active_connections.values():
            count += len(connections)
        return count
    
    def get_session_count(self) -> int:
        """Get number of active sessions"""
        return len(self.active_connections)

# Global instance
websocket_manager = WebSocketManager()