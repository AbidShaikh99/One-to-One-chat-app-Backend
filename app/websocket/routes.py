from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db import models
from app.websocket.user import ConnectionUser

router = APIRouter()
user = ConnectionUser()


@router.websocket("/ws/{user_id}")
async def websocket_chat(websocket: WebSocket, user_id: int, db: Session = Depends(get_db)):
    
    await user.connect(user_id, websocket)

    messages = db.query(models.Message).filter(
        (models.Message.sender_id == user_id) |
        (models.Message.receiver_id == user_id)
    ).order_by(models.Message.timestamp).all()

    history = []
    for msg in messages:
        history.append({
            "sender_id": msg.sender_id,
            "receiver_id": msg.receiver_id,
            "sender_name": msg.sender.name,
            "receiver_name": msg.receiver.name,
            "content": msg.content,
            "timestamp": str(msg.timestamp)
        })

    await websocket.send_json({
        "type": "history",
        "data": history
    })

    try:
        while True:
            data = await websocket.receive_json()

            receiver_id = data["receiver_id"]
            content = data["content"]

            sender = db.query(models.User).filter(models.User.id == user_id).first()
            receiver = db.query(models.User).filter(models.User.id == receiver_id).first()

            if not sender or not receiver:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid sender or receiver"
                })
                continue

            message = models.Message(
                sender_id=user_id,
                receiver_id=receiver_id,
                content=content
            )
            db.add(message)
            db.commit()
            db.refresh(message)

            messages = db.query(models.Message).filter(
                (
                    (models.Message.sender_id == user_id) &
                    (models.Message.receiver_id == receiver_id)
                ) |
                (
                    (models.Message.sender_id == receiver_id) &
                    (models.Message.receiver_id == user_id)
                )
            ).order_by(models.Message.timestamp).all()

            updated_history = []
            for msg in messages:
                updated_history.append({
                    "sender_id": msg.sender_id,
                    "receiver_id": msg.receiver_id,
                    "sender_name": msg.sender.name,
                    "receiver_name": msg.receiver.name,
                    "content": msg.content,
                    "timestamp": str(msg.timestamp)
                })

            await user.send_message(receiver_id, {
                "type": "history",
                "data": updated_history
            })

            await user.send_message(user_id, {
                "type": "history",
                "data": updated_history
            })

    except WebSocketDisconnect:
        user.disconnect(user_id)