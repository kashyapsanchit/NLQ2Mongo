import uvicorn
from src.backend import app

if __name__ == "__main__":
    uvicorn.run("src.backend:app", host="0.0.0.0", port=8000, reload=True)
