from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Client connected")

    try:
        while True:
            message = await websocket.receive_text()
            response = f"Server received: {message}"
            await websocket.send_text(response)

    except WebSocketDisconnect:
        print("Client disconnected")