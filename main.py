from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette import status
from routers import auth, users, books, admin, home


app = FastAPI(title="Books application bundled with N8N", version="1.0.0")

app.mount("/static", StaticFiles(directory="static"), name="static")


app.include_router(home.router)
app.include_router(auth.router)
app.include_router(books.router)
app.include_router(users.router)
app.include_router(admin.router)


@app.get("/healthy", status_code=status.HTTP_200_OK)
async def get_health():
    return {"status": "Healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
