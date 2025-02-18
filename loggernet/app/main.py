from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Query,Path
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import subprocess
from sqlalchemy.orm import Session
import uuid
import os
from app import schemas
from app.instruments import INSTRUMENTS, Instrument
from typing import Annotated, Any

app = FastAPI()
app.mount("/static", StaticFiles(directory="/app/app/static"), name="static")

@app.get("/static")
async def read_root():
    return FileResponse(os.path.join("/app/app/static", "index.html"))

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
            if "Compiled in" in output:
                return JSONResponse(
                    content={"message": "Compilation succeeded", "output": output},
                    status_code=200,
                )

            return JSONResponse(
                content={"message": "Compilation failed", "details": output},
                status_code=400,
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


@app.get("/instruments")
async def get_instruments(q: Annotated[schemas.NamesOnly, Query()]):
    if q.names_only:
        return {'instruments': list(INSTRUMENTS.keys())}
    instances = {}
    for name, instrument in INSTRUMENTS.items():
        instances[name] = instrument(elevation=1, sdi12_address=1).to_json()
    return instances


@app.get("/instruments/{instrument}")
async def get_instrument(instrument: Annotated[schemas.ValidInstruments, Path]):
    instance = INSTRUMENTS[instrument.value](elevation=1, sdi12_address=1)
    
    out = instance.to_json()
    return out


@app.post("/program")
async def build_program(
    instrument: Annotated[list[schemas.ValidInstruments], Query(..., help="A list of instruments you would like to build a program for.")]
):
    
    #TODO: this
    ...

@app.get("/program/{station}")
async def build_program_from_station(
    station: str
):
    #TODO: This
    ...


@app.get("/program/build")
async def program_builder_form():
    # TODO: simple html form that hist the "/program" endpoint
    ...