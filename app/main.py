from fastapi import FastAPI
from app.websocket.routes import router as websocket_router
from app.websocket.auth import router as auth_router
from app.db.database import Base, engine

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(websocket_router)
app.include_router(auth_router)