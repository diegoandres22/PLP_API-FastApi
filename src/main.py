from fastapi import FastAPI
from src.db.db import session
from src.models.todo import Todo

app = FastAPI()

@app.post("/")
async def create_todo(text: str, is_done: bool = False):

    todo = Todo(text=text, is_done=is_done)
    session.add(todo)
    session.commit()
    return { "Todo creado": todo.text }


@app.get("/")
def read_root():
    return {"Hello World"}