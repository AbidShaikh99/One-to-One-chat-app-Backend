from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db import models
from app.websocket.user import ConnectionUser

router = APIRouter()
manager = ConnectionUser()

@router.websocket("/ws/{user_id}")
async def websocket_chat(websocket: WebSocket, user_id: int, db: Session = Depends(get_db)):
    await manager.connect(user_id, websocket)

    try:
        while True:
            data = await websocket.receive_json()

            receiver_id = data["receiver_id"]
            content = data["content"]

            sender = db.query(models.User).filter(models.User.id == user_id).first()
            receiver = db.query(models.User).filter(models.User.id == receiver_id).first()

            message = models.Message(
                sender_id=user_id,
                receiver_id=receiver_id,
                content=content
            )
            db.add(message)
            db.commit()

            response = {
                "sender_name": sender.name,
                "receiver_name": receiver.name,
                "content": content,
                "timestamp": str(message.timestamp)
            }

            await manager.send_message(receiver_id, response)

            await manager.send_message(user_id, response)

    except WebSocketDisconnect:
        manager.disconnect(user_id)