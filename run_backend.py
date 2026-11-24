"""
FastAPI Server Runner
Project Code: PRJ-042 | Follow-up Reply Assistant
"""

import uvicorn
from backend.config import settings

if __name__ == "__main__":
    print(f"Starting Follow-up Reply Assistant API ({settings.PROJECT_CODE})...")
    print(f"Swagger Documentation available at: http://{settings.HOST}:{settings.PORT}/docs")
    print(f"Student: {settings.STUDENT_NAME} ({settings.REG_NO}) - {settings.DEPARTMENT}")
    uvicorn.run("backend.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
