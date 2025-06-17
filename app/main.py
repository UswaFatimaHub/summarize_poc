from fastapi import FastAPI
from app.routes import processconversation, file_ops
import os
import uvicorn

from app.core.logger import logger, setup_logging

setup_logging()

app = FastAPI(title="Conversation Summarizer API")

app.include_router(file_ops.router, prefix="/api/file", tags=["File Operations"])
app.include_router(processconversation.router, prefix="/api", tags=["Summarization"])

@app.get("/")
def read_root():
    logger.info("Root accessed")
    return {"message": "Hello"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True) #uvicorn app.main:app --reload