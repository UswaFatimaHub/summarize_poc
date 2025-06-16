from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.services.summarizer import summarize_by_opportunity_id
from app.config import UPLOAD_DIR, SUMMARY_DIR
import os
import json
from typing import Optional

router = APIRouter()

@router.get("/summary/{opportunity_id}")
def get_summary_by_opportunity(opportunity_id: str):
    result = summarize_by_opportunity_id(float(opportunity_id))  

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return {
        "opportunity_id": opportunity_id,
        "summary": result["summary"]
    }


