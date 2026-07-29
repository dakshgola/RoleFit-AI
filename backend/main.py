import os
import sys
import json
import asyncio
import shutil
from typing import Generator
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

# Ensure local backend modules can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pipeline import run_placement_pipeline

app = FastAPI(title="PlacementPrep AI Backend API")

# Configure CORS origins
allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://rolefit-ai.vercel.app"
]

frontend_env = os.getenv("FRONTEND_URL")
if frontend_env and frontend_env.rstrip("/") not in allowed_origins:
    allowed_origins.append(frontend_env.rstrip("/"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    print(f"[CORS] Configured allowed origins: {allowed_origins}")

@app.post("/analyze")
async def analyze_placement(
    company: str = Form(...),
    role: str = Form(...),
    jd_text: str = Form(...),
    resume_file: UploadFile = File(...),
    company2: str = Form(None)
):
    # Determine local workspace paths
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    temp_dir = os.path.join(root_dir, "temp")
    os.makedirs(temp_dir, exist_ok=True)
    temp_resume_path = os.path.join(temp_dir, resume_file.filename)
    
    # Save the uploaded file locally so we can read it
    with open(temp_resume_path, "wb") as buffer:
        shutil.copyfileobj(resume_file.file, buffer)
        
    # Queue for transferring progress status events from synchronous pipeline to async generator
    event_queue = asyncio.Queue()
    loop = asyncio.get_running_loop()
    
    # Callback execution within the pipeline thread
    def pipeline_callback(step: str, status: str):
        asyncio.run_coroutine_threadsafe(
            event_queue.put({"type": "status", "step": step, "status": status}),
            loop
        )
        
    # Async pipeline task running in the thread pool
    async def run_pipeline():
        try:
            # Parse resume PDF text content
            from tools import parse_resume
            resume_text = parse_resume.invoke(temp_resume_path)
            
            if resume_text.startswith("Error"):
                raise ValueError(resume_text)
                
            await asyncio.sleep(0.5)
            
            # Execute synchronous pipeline in FastAPI executor pool
            result_state = await loop.run_in_executor(
                None,
                lambda: run_placement_pipeline(
                    company=company,
                    role=role,
                    jd_text=jd_text,
                    resume_text=resume_text,
                    callback=pipeline_callback,
                    company2=company2
                )
            )
            
            # Send compiled results payload
            await event_queue.put({
                "type": "result",
                "data": {
                    "company_research": result_state.get("company_research", ""),
                    "interview_patterns": result_state.get("interview_patterns", ""),
                    "skill_gap": result_state.get("skill_gap", ""),
                    "report": result_state.get("final_report", "")
                }
            })
        except Exception as err:
            await event_queue.put({
                "type": "error",
                "message": str(err)
            })
        finally:
            # Clean up temp resume PDF
            if os.path.exists(temp_resume_path):
                try:
                    os.remove(temp_resume_path)
                except Exception:
                    pass
            # End the stream
            await event_queue.put(None)

    # Start execution task in background
    asyncio.create_task(run_pipeline())
    
    # Event yield stream
    async def sse_generator():
        while True:
            event = await event_queue.get()
            if event is None:
                break
            yield f"data: {json.dumps(event)}\n\n"
            
    return StreamingResponse(sse_generator(), media_type="text/event-stream")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
