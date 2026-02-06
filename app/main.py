from fastapi import FastAPI
from app.api.endpoints import router as api_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=f"Developed by {settings.DEVELOPER}"
)

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {
        "message": "Welcome to AI Market Trend Analyzer API",
        "developer": settings.DEVELOPER,
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
