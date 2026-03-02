from fastapi import FastAPI
from typing import Optional

app = FastAPI()

@app.get("/search")
def search(name: Optional[str] = None, age: Optional[int] = None):
    return {
        "name": name,
        "age": age
    }