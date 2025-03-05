from fastapi import WebSocket

class WebsocketManager:
    connections: dict[int, list[WebSocket]]

    def __init__(self) -> None:
        self.connections = {}

    async def connect(self, websocket: WebSocket, client_id: int):
        if client_id not in self.connections:
            self.connections[client_id] = []

        await websocket.accept()
        self.connections[client_id].append(websocket)

    async def send_message(self, client_id: int, message: object):
        if client_id not in self.connections:
            return

        print(self.connections)
        failed_connections = []

        for connection in self.connections[client_id]:
            try:
                print(connection.client_state)
                await connection.send_json(message)
            except Exception as e:
                print(e)
                failed_connections.append(connection)

        # Remove failed connections after iteration
        for connection in failed_connections:
            self.connections[client_id].remove(connection)

    async def broadcast(self, data: object):
        for client_id in self.connections:
            for i in range(len(self.connections[client_id])):
                connection = self.connections[client_id][i]
                try:
                    await connection.send_json(data)
                except Exception:
                    self.connections[client_id].pop(i)

websocket_manager = WebsocketManager()