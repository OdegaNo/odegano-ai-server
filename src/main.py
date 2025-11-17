from fastapi import FastAPI

from src.categories.extractor import extract_place_traits

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/traits")
async def traits(request: str):
    return (
        {
            "message": "traits extracted",
            "data": extract_place_traits(request)
        },
        200,
    )


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
