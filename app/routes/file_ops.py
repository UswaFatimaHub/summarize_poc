from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os
from app.config import UPLOAD_DIR
from app.utils.file_io import delete_existing_file
from app.db import insert_csv_to_mongo, purge_collection
from io import StringIO
router = APIRouter()

@router.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed.")
    
    file_content = await file.read()
    csv_data = StringIO(file_content.decode("utf-8"))

    # filepath = os.path.join(UPLOAD_DIR, file.filename)
    # with open(filepath, "wb") as f:
    #     f.write(await file.read())

    result = insert_csv_to_mongo(csv_path=csv_data, collection_name="conversations")
    
    return {"message": "File uploaded successfully", "filename": file.filename, "records_added": result.get("inserted_count", 0), "error": result.get("error", None)}


@router.delete("/purge")    
def purge():
    result = purge_collection()
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return {"message": f"Purged {result['deleted_count']} records."}