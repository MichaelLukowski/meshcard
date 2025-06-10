"""
Usage:
- Run app: python run.py
"""

import uvicorn

import cdislogging
from src.logger import LOG_LEVEL

# Apply cdis-logging format to uvicorn when running locally
cdislogging.get_logger(None, log_level="debug")
for logger_name in ["uvicorn", "uvicorn.error", "uvicorn.access"]:
    cdislogging.get_logger(
        logger_name, log_level="debug" if LOG_LEVEL == "debug" else "info"
    )

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, log_config=None)
