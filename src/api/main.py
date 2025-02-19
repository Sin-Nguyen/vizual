from fastapi import FastAPI, UploadFile, File, Request, Body
import uvicorn
import os
import json
import logging
from core.paddleocr_tesseract import extract_structured_data, find_and_draw
from core.adb_actions import execute_actions, process_ocr_results

app = FastAPI()
port = 4721
app.logger = logging.getLogger("uvicorn")
app.logger.setLevel(logging.INFO)

app.config = {"MAX_CONTENT_LENGTH": 20 * 1024 * 1024}  # 20MB limit
UPLOAD_DIR = "uploads"
ANNOTATED_DIR = "annotated_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(ANNOTATED_DIR, exist_ok=True)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    response = await call_next(request)
    app.logger.info(f"Endpoint: {request.url.path}")
    return response

@app.get("/")
async def home():
    return {"message": "OpenCV still alive!"}

@app.post("/ocr")
async def ocr_process(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    return extract_structured_data(file_path)

@app.post("/ocr-search")
async def ocr_process_with_search(file: UploadFile = File(...), target_text: str = Body(...)):
    """OCR processing with specific text search."""
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    return find_and_draw(file_path, target_text)

@app.post("/batch-ocr")
async def batch_ocr_process(files: list[UploadFile] = File(...)):
    file_paths = []
    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
        file_paths.append(file_path)
    results = batch_process_images(file_paths)
    return results

@app.post("/execute-adb")
async def execute_adb(actions: list[dict] = Body(...)):
    """API endpoint to execute custom ADB actions."""
    try:
        execute_actions(actions)
        return {"status": "success", "executed_actions": actions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/execute-ocr-adb")
async def execute_ocr_adb(ocr_results: dict = Body(...), target_texts: list[str] = Body([])):
    """API endpoint to process OCR results and trigger ADB actions."""
    try:
        actions = process_ocr_results(ocr_results, target_texts)
        execute_actions(actions)
        return {"status": "success", "executed_actions": actions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))