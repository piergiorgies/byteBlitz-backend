from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, WebSocket

from app.database import get_session
from app.models import Role
from app.util.jwt import get_websocket_user
from app.models.mapping.user import User
from app.util.websocket import websocket_manager
from app.controllers.general import get_dashboard_stats

ws = APIRouter(
    prefix="/general",
    tags=["General"],
)

@ws.websocket("/ws")
async def websocket(socket: WebSocket, user: Annotated[User, Depends(get_websocket_user)]):
    await websocket_manager.connect(socket, user.id)
    # to keep the connection alive
    while True:
        if socket.client_state.name != "CONNECTED":
            websocket_manager.disconnect(user.id)
            break
        data = await socket.receive()
        print(f"Received data from user {user.id}: {data}")

router = APIRouter(
    tags=["General"],
)

@router.get("/dashboard/stats", summary="Get dashboard statistics")
async def dashboard_stats(session=Depends(get_session)):
    """
    Get dashboard statistics
    """
    try:
        return get_dashboard_stats(session)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))


