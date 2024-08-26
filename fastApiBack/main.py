from fastapi import FastAPI
from components.database import Base,engine
from fastapi.middleware.cors import CORSMiddleware
from components.routes import router
import uvicorn

Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost:8501", 
    "http://127.0.0.1:8501", 
    "http://192.168.231.80:8501"
]

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this as needed for frontend deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router,prefix="/loan")
