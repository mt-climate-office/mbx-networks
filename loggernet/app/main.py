from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse
import subprocess
from sqlalchemy.orm import Session
import uuid
import os

from app.db import get_db, init_db, Instruments


app = FastAPI()


# Lifespan event to initialize the database
@app.on_event("startup")
def startup_event():
    init_db()


# POST endpoint to add a new record
@app.post("/instrument/")
def create_record(
    long_name: str, short_name: str, data: dict, db: Session = Depends(get_db)
):
    record_id = str(uuid.uuid4())  # Generate a unique ID
    new_record = Instruments(
        id=record_id, long_name=long_name, short_name=short_name, data=data
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return {"id": record_id, "message": "Record created successfully"}


# GET endpoint to fetch a record by short_name
# TODO: Swap this to use instruments.py rather than db.
@app.get("/instrument/{short_name}")
def get_record(short_name: str, db: Session = Depends(get_db)):
    record = db.query(Instruments).filter(Instruments.short_name == short_name).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return {
        "id": record.id,
        "long_name": record.long_name,
        "short_name": record.short_name,
        "data": record.data,
    }


@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications! Testing!!!!!"}


@app.post("/compile")
async def check_compile(file: UploadFile = File(...)):
    # Save the uploaded file temporarily
    temp_file_path = f"/home/wine/{file.filename}"
    try:
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(await file.read())

        # Use subprocess to run the `check_compile` command
        try:
            output = subprocess.check_output(
                ["check_compile", temp_file_path],
                stderr=subprocess.STDOUT,
                text=True,
                cwd="/home/wine",
            )
            if "Failed" in output:
                return JSONResponse(
                    content={"message": "Compilation failed", "details": output},
                    status_code=400,
                )
            return JSONResponse(
                content={"message": "Compilation succeeded", "output": output},
                status_code=200,
            )
        except subprocess.CalledProcessError as e:
            # Handle errors from the command
            return JSONResponse(
                content={"error": "Compilation check failed", "details": e.output},
                status_code=400,
            )

    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
