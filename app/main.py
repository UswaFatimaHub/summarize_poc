from fastapi import FastAPI
from app.routes import summarize, file_ops

app = FastAPI(title="Conversation Summarizer API")

app.include_router(file_ops.router, prefix="/api/file", tags=["File Operations"])
app.include_router(summarize.router, prefix="/api", tags=["Summarization"])
