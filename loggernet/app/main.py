from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import subprocess
import os

app = FastAPI()

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
            output = subprocess.check_output(["check_compile", temp_file_path], stderr=subprocess.STDOUT, text=True, cwd="/home/wine")
            if "Failed" in output:
                return JSONResponse(content={"message": "Compilation failed", "details": output}, status_code=400)
            return JSONResponse(content={"message": "Compilation succeeded", "output": output}, status_code=200)
        except subprocess.CalledProcessError as e:
            # Handle errors from the command
            return JSONResponse(content={"error": "Compilation check failed", "details": e.output}, status_code=400)
    
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)