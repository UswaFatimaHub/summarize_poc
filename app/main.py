from fastapi import FastAPI
from app.routes import summarize, file_ops
import os
import uvicorn


app = FastAPI(title="Conversation Summarizer API")

app.include_router(file_ops.router, prefix="/api/file", tags=["File Operations"])
app.include_router(summarize.router, prefix="/api", tags=["Summarization"])



if __name__ == "__main__":
    # Get port from environment or use 8000 as default
    port = int(os.environ.get("PORT", 8000))
    # host = os.environ.get("HOST", "0.0.0.0")

    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)