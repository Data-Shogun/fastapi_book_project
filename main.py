from fastapi import FastAPI
from routers import auth, users


app = FastAPI(title="Books application bundled with N8N", version="1.0.0")


app.include_router(auth.router)
app.include_router(users.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
