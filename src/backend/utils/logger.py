import logging
from fastapi import FastAPI

def create_logger():
    logger = logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("app.log"),  # Log to a file
            logging.StreamHandler()          # Log to the console
        ]
    )
    return logger

logger = create_logger()
