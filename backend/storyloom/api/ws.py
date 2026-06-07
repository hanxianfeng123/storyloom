from fastapi import APIRouter, WebSocket

router = APIRouter()


@router.websocket("/ws/pipeline/{pipeline_id}")
async def pipeline_ws(websocket: WebSocket, pipeline_id: str):
    await websocket.accept()
    try:
        while True:
            await websocket.receive_json()
            # Echo back for now; will push stage progress
            await websocket.send_json({"status": "progress", "pipeline_id": pipeline_id})
    except Exception:
        await websocket.close()
