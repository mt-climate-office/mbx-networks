from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Query,Path, Body
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import subprocess
from sqlalchemy.orm import Session
import uuid
import os
from app import schemas
from app.instruments import INSTRUMENTS, Instrument
from app.program import Program, elev_sdi12_rename, soil_slow_seq_match
import datetime as dt
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
    for _, instrument in INSTRUMENTS.items():
        instances[instrument._id] = instrument(elevation=1, sdi12_address=1).to_json()
    return instances


@app.get("/instruments/{instrument}")
async def get_instrument(instrument: Annotated[schemas.ValidInstruments, Path]):
    instance = INSTRUMENTS[instrument.value](elevation=1, sdi12_address=1)
    
    out = instance.to_json()
    return out

# my_sensors = [
#     Vaisala_HMP155(200),
#     Acclima_TDR310N(5, "1", transform=lambda x: elev_sdi12_rename(x, 'both')),
#     Acclima_TDR310N(5, "a", transform=lambda x: elev_sdi12_rename(x, 'both')),
#     Acclima_TDR310N(10, "2", transform=lambda x: elev_sdi12_rename(x, 'both')),
#     Acclima_TDR310N(10, "b", transform=lambda x: elev_sdi12_rename(x, 'both')),
#     RMYoung_05108_77(1000),
# ]

# program = Program(
#     "test program", my_sensors, "SequentialMode", True, transform=soil_slow_seq_match
# )

def find_instrument(target: str, instruments: list[schemas.ProgramInstruments]) -> schemas.ProgramInstruments | None:
    for instrument in instruments:
        if instrument._id == target:
            return instrument
    return None

@app.post("/program")
async def build_program(
    instruments: Annotated[list[schemas.ProgramInstruments],Body()]
):
    program_instruments = []
    for instrument in instruments:
        instance = INSTRUMENTS[instrument.name](
            elevation = instrument.elevation,
            sdi12_address = instrument.sdi12_address
        )

        if instance.wires:
            for wire in instance.wires.args:
                user_def_wiring = instrument.wiring[wire.wire]
                wire.port = user_def_wiring
            
        program_instruments.append(instance)
    
    for instrument in instruments:
        if not instrument.dependencies:
            continue
        for dep, meta in instrument.dependencies.items():

            # Find the instances of instrument that will populate the program
            program_instrument = find_instrument(instrument.name, program_instruments)
            target = find_instrument(meta["_id"], program_instruments)
            if target is None:
                raise HTTPException(
                    status_code=400,
                    detail=f"Could not find dependency {meta['_id']} for {instrument.name}",
                )
            
            # Add the dependency to the instrument
            the_dep = target.variables[meta['variable']]
            program_instrument.dependencies.map_dependency(meta['variable'], the_dep)
    
    program = Program(
        f"CSI_LoggerNet_{str(dt.date.today()).replace("-", "")}.CR1X",
        instruments = program_instruments,
        mode="SequentialMode",
    )

    out = program.construct()
    # TODO: Fix If logic to str here.
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