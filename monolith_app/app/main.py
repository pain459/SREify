from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from db import get_connection, init_db
from contextlib import asynccontextmanager

# app = FastAPI()

# Initialize DB at startup
# @app.on_event("startup")
# def startup():
#     init_db()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

class Item(BaseModel):
    name: str
    description: str = None

@app.get("/")
def read_root():
    return {"status": "API is live!"}

@app.get("/items")
def get_items():
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM items").fetchall()
        return [dict(row) for row in rows]

@app.post("/items")
def create_item(item: Item):
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO items (name, description) VALUES (?, ?)",
            (item.name, item.description)
        )
        conn.commit()
        item_id = cur.lastrowid
        return {"id": item_id, **item.model_dump()}
