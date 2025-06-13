from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.services.summarizer import summarize_opportunities
from app.config import UPLOAD_DIR, SUMMARY_DIR
import os
import json
from typing import Optional

router = APIRouter()

@router.post("/summarize")
def trigger_summarization(filename: str):
    filepath = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Uploaded file not found.")
    
    summary_path = summarize_opportunities(filepath)

    if not os.path.exists(summary_path):
        raise HTTPException(status_code=500, detail="Summary file not generated.")

    return FileResponse(
        path=summary_path,
        filename=os.path.basename(summary_path),
        media_type="application/json"
    )
    

def load_latest_summary_file() -> Optional[str]:
    files = [f for f in os.listdir(SUMMARY_DIR) if f.startswith("summaries_") and f.endswith(".json")]
    if not files:
        return None
    files.sort(reverse=True)
    return os.path.join(SUMMARY_DIR, files[0])

@router.get("/summary/{opportunity_id}")
def get_summary_by_opportunity(opportunity_id: str):
    summary_file = load_latest_summary_file()

    if not summary_file or not os.path.exists(summary_file):
        raise HTTPException(status_code=404, detail="No summary file found.")

    with open(summary_file, "r", encoding="utf-8") as f:
        summaries = json.load(f)

    if opportunity_id not in summaries:
        raise HTTPException(status_code=404, detail=f"Opportunity ID {opportunity_id} not found.")

    return {
        "opportunity_id": opportunity_id,
        "summary": summaries[opportunity_id]
    }



