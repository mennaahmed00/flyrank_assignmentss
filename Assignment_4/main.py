
#import necessary libraries
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from supabase import create_client, Client
from fastapi import FastAPI

load_dotenv()

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(url,key)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Server running and connected to Supabase")
    yield

app= FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"status": "API is online"}