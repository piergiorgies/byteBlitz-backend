from typing import Annotated
from fastapi import APIRouter, Depends, WebSocket

from app.util.jwt import get_websocket_user
from app.models.mapping.user import User
from app.util.websocket import websocket_manager

router = APIRouter(
    prefix="/general",
    tags=["General"],
)

@router.websocket("/ws")
async def websocket(socket: WebSocket, user: Annotated[User, Depends(get_websocket_user)]):
    await websocket_manager.connect(socket, user.id)
    # to keep the connection alive
    while True:
        data = await socket.receive()
