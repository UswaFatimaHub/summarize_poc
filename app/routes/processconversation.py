from fastapi import APIRouter, HTTPException
from app.handler.conv_handler import processconv_by_opportunity_id

router = APIRouter()

@router.get("/process_conv/{opportunity_id}")
def process_by_opportunity(opportunity_id: str):
    result = processconv_by_opportunity_id(float(opportunity_id))  

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return {
        "result": result
    }


