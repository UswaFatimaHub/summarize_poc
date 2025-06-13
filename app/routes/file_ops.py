from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os
from app.config import UPLOAD_DIR
from app.utils.file_io import delete_existing_file

router = APIRouter()

@router.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed.")
    
    filepath = os.path.join(UPLOAD_DIR, file.filename)
    with open(filepath, "wb") as f:
        f.write(await file.read())
    
    return {"message": "File uploaded successfully", "filename": file.filename}


@router.post("/delete")
def delete_uploaded_file(filename: str):
    if delete_existing_file(filename):
        return {"message": f"File '{filename}' deleted."}
    else:
        raise HTTPException(status_code=404, detail="File not found.")
