from fastapi import FastAPI

app = FastAPI(title="Storyloom")


@app.get("/health")
async def health():
    return {"status": "ok"}
