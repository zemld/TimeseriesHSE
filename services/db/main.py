from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import date
from typing import Dict
from database_manager import DatabaseManager

db_manager = FastAPI()
db = DatabaseManager("timescaledb", 5432, "db", "user", "secret")


class InsertDataRequest(BaseModel):
    table_name: str
    data: Dict[date, float]


class SelectDataRequest(BaseModel):
    table_name: str
    from_date: date
    till_date: date


class DeleteDataRequest(BaseModel):
    table_name: str
    till_date: str


@db_manager.post("/create_table")
async def create_table(table_name: str):
    try:
        await db.create_table(table_name)
        return {"message": f"Table {table_name} created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@db_manager.post("/insert_data")
async def insert_data(request: InsertDataRequest):
    try:
        await db.insert_data(request.table_name, request.data)
        return {"message": "Data inserted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@db_manager.post("/delete_data")
async def delete_data(request: DeleteDataRequest):
    try:
        await db.delete_data(request.table_name, request.till_date)
        return {"message": "Data deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@db_manager.get("/select_data")
async def select_data(request: SelectDataRequest):
    try:
        data = await db.select_data(
            request.table_name, request.from_date, request.till_date
        )
        return {"data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
