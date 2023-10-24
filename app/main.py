# from fastapi import FastAPI


# app=FastAPI()

# @app.get('/')
# async def index():
#     return {"Real":"Python :)"}
# Importar módulos necesarios
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from databases import Database
from sqlalchemy import create_engine, Column, Integer, String, Date, MetaData, update, delete
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import sessionmaker
import asyncio
from datetime import date


# Cadena de conexión a la base de datos
DATABASE_URL = "postgresql+asyncpg://doadmin:AVNS_omvuLIQKKVwAoV5PcZ5@ivillarroelr-do-user-14586701-0.b.db.ondigitalocean.com:25060/defaultdb"

# Inicializar la conexión a la base de datos
database = Database(DATABASE_URL)
metadata = MetaData()

# Crear el modelo base de SQLAlchemy
Base: DeclarativeMeta = declarative_base(metadata=metadata)

# Definir el modelo de SQLAlchemy para Tarea
class TaskInDB(Base):
    __tablename__ = 'karitask'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    due_date = Column(Date)
    status = Column(String)

# Definir el modelo Pydantic para Tarea
class Task(BaseModel):
    id: int
    name: str
    description: str
    due_date: date
    status: str

# Definir el modelo Pydantic para crear una nueva Tarea
class TaskCreate(BaseModel):
    name: str
    description: str
    due_date: date
    status: str

# Inicializar la aplicación FastAPI
app = FastAPI()

# Evento para ejecutar cuando la aplicación inicia
@app.on_event("startup")
async def startup():
    await database.connect()

# Evento para ejecutar cuando la aplicación se apaga
@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Endpoint para crear una nueva tarea
@app.post("/karitask/", response_model=Task)
async def create_task(task: TaskCreate):
    query = TaskInDB.__table__.insert().values(**task.dict())
    last_record_id = await database.execute(query)
    return {**task.dict(), "id": last_record_id}

# Endpoint para actualizar una tarea existente por ID
@app.put("/karitask/{task_id}/", response_model=Task)
async def update_task(task_id: int, task: TaskCreate):
    query = (
        update(TaskInDB.__table__)
        .where(TaskInDB.id == task_id)
        .values(**task.dict())
        .returning(TaskInDB)
    )
    updated_task = await database.fetch_one(query)
    if not updated_task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return {**updated_task}

# Endpoint para eliminar una tarea por ID
@app.delete("/karitask/{task_id}/", response_model=Task)
async def delete_task(task_id: int):
    query = delete(TaskInDB.__table__).where(TaskInDB.id == task_id).returning(TaskInDB)
    deleted_task = await database.fetch_one(query)
    if not deleted_task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return {**deleted_task}

# Endpoint para listar todas las tareas
@app.get("/karitask/", response_model=list[Task])
async def read_karitask(skip: int = 0, limit: int = 10):
    query = TaskInDB.__table__.select().offset(skip).limit(limit)
    karitask = await database.fetch_all(query)
    return karitask

# Endpoint para obtener una tarea por ID
@app.get("/karitask/{task_id}/", response_model=Task)
async def read_task(task_id: int):
    query = TaskInDB.__table__.select().where(TaskInDB.id == task_id)
    task = await database.fetch_one(query)
    if task is None:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return task
