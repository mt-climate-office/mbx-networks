from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
import subprocess
from sqlalchemy.orm import Session
import uuid
import os
from app.schemas import valid_instruments
from app.instruments import INSTRUMENTS, Instrument
from typing import Annotated

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
async def get_instruments():
    instances = []
    for name, instrument in INSTRUMENTS.items():
        instances.append(instrument(elevation=1, sdi12_address=1))
        ...
    # TODO: Make this return a nice json response of each instrument
    return {"cool": "stuff"}


@app.get("/instruments/{instrument}")
async def get_instrument(instrument: valid_instruments):
    instance = INSTRUMENTS[instrument](elevation=1, sdi12_address=1)
    # TODO: Make this return a nice json response of each instrument

    return instance


@app.get("/program")
async def build_program(
    instrument: Annotated[list[Instrument], Query(..., help="A list of instruments you would like to build a program for.")]
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