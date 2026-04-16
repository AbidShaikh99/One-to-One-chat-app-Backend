from fastapi import WebSocket

class ConnectionUser:
    
    def __init__(self):
        self.active_connections = {}
        
    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket
    
    async def disconnect(self, user_id: int):
        self.active_connections.pop(user_id, None)
    
    async def send_message(self, user_id:str, message: dict):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_json(message)
    