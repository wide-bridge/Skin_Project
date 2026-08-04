from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app import config
from app.consultation_service import handle_consultation


app = FastAPI(title="Skin Diagnosis & Makeup Consultation PoC")

app.mount("/static", StaticFiles(directory=str(config.PROJECT_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(config.PROJECT_DIR / "templates"))


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "model_path": str(config.MODEL_PATH) if config.MODEL_PATH else None,
        "rag_engine": "faiss",
    }


@app.post("/api/chat")
async def chat(
    message: str = Form(""),
    mode: str = Form("skin"),
    image: UploadFile | None = File(None),
):
    try:
        image_bytes = await image.read() if image and image.filename else None
        response = handle_consultation(message=message, image_bytes=image_bytes, mode=mode)
        return response.model_dump()
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={
                "error": str(exc),
                "answer": "Request processing failed. Please check the model file, FAISS, and API key settings.",
            },
        )
