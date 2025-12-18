from fastapi import FastAPI


app = FastAPI(
    title="Books application bundled with N8N",
    version="1.0.0"
)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000
    )