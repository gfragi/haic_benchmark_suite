# This file is used to run the FastAPI application.
# alias in the root of backend


from app.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
