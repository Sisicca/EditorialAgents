from fastapi import FastAPI
from .routers import process_router
# Remove or conditionally enable CORS if running frontend on a different port during development
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Editorial Agents API")

# CORS (Cross-Origin Resource Sharing) - Be cautious with allowed_origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins. For production, restrict this.
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.).
    allow_headers=["*"],  # Allows all headers.
)

app.include_router(process_router.router, prefix="/api/process", tags=["Process Management"])

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}

# Potentially load main configuration here if needed globally
# from editorial_agents_project.config import load_config # Adjust import path
# global_config = load_config()
