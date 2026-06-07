from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from storyloom.api.routes import projects, pipeline, memory, chapters
from storyloom.api import ws

app = FastAPI(title="Storyloom", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(pipeline.router, prefix="/api/pipeline", tags=["pipeline"])
app.include_router(memory.router, prefix="/api/memory", tags=["memory"])
app.include_router(chapters.router, prefix="/api/chapters", tags=["chapters"])
app.include_router(ws.router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
