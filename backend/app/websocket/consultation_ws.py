import json
import secrets
from typing import Dict, List
from fastapi import WebSocket, WebSocketDisconnect
from backend.app.database.database import execute_query

class ConsultationConnectionManager:
    def __init__(self):
        # Map consultation_id -> list of active WebSocket connections
        self.active_rooms: Dict[str, List[WebSocket]] = {}

    async def connect(self, consultation_id: str, websocket: WebSocket):
        await websocket.accept()
        if consultation_id not in self.active_rooms:
            self.active_rooms[consultation_id] = []
        self.active_rooms[consultation_id].append(websocket)

    def disconnect(self, consultation_id: str, websocket: WebSocket):
        if consultation_id in self.active_rooms:
            if websocket in self.active_rooms[consultation_id]:
                self.active_rooms[consultation_id].remove(websocket)
            if not self.active_rooms[consultation_id]:
                del self.active_rooms[consultation_id]

    async def broadcast_to_room(self, consultation_id: str, message: dict, sender_ws: WebSocket = None):
        if consultation_id in self.active_rooms:
            for connection in self.active_rooms[consultation_id]:
                # Send to all participants, or exclude sender for peer-to-peer signaling
                if sender_ws and connection == sender_ws and message.get("type") in ["signal", "ice_candidate"]:
                    continue
                try:
                    await connection.send_text(json.dumps(message))
                except Exception:
                    pass

ws_manager = ConsultationConnectionManager()

async def handle_consultation_websocket(websocket: WebSocket, consultation_id: str):
    await ws_manager.connect(consultation_id, websocket)
    try:
        # Send room connection confirmation
        await websocket.send_text(json.dumps({
            "type": "system",
            "message": "Connected to secure teleconsultation room.",
            "consultation_id": consultation_id
        }))
        
        while True:
            data_text = await websocket.receive_text()
            try:
                data = json.loads(data_text)
            except Exception:
                continue

            msg_type = data.get("type")
            
            if msg_type == "chat":
                # Persist chat message to database
                sender_id = data.get("sender_id", "anonymous")
                sender_name = data.get("sender_name", "User")
                sender_role = data.get("sender_role", "PATIENT")
                text_content = data.get("message", "")
                
                msg_id = f"msg_{secrets.token_hex(6)}"
                execute_query("""
                    INSERT INTO consultation_messages (id, consultation_id, sender_id, sender_name, sender_role, message)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (msg_id, consultation_id, sender_id, sender_name, sender_role, text_content))
                
                # Broadcast chat message with ID and timestamp
                await ws_manager.broadcast_to_room(consultation_id, {
                    "type": "chat",
                    "id": msg_id,
                    "sender_id": sender_id,
                    "sender_name": sender_name,
                    "sender_role": sender_role,
                    "message": text_content,
                    "timestamp": data.get("timestamp")
                })
                
            elif msg_type in ["signal", "ice_candidate", "call_state", "low_bandwidth_toggle"]:
                # Relay WebRTC signaling directly to peer
                await ws_manager.broadcast_to_room(consultation_id, data, sender_ws=websocket)

    except WebSocketDisconnect:
        ws_manager.disconnect(consultation_id, websocket)
        await ws_manager.broadcast_to_room(consultation_id, {
            "type": "system",
            "message": "A participant has disconnected from the room."
        })
