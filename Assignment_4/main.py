
#import necessary libraries
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from supabase import create_client, Client
from fastapi import FastAPI,HTTPException, status
from pydantic import BaseModel





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


class UserCredentials(BaseModel):
    email: str
    password: str

@app.post("/auth/signup", status_code = status.HTTP_201_CREATED)

def signup(credentials: UserCredentials):
    try:
        response = supabase.auth.sign_up({
            "email": credentials.email,
            "password": credentials.password
        })
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
@app.post("/auth/login")
def login(credentials: UserCredentials):
        try:
            response = supabase.auth.sign_in_with_password({
                "email": credentials.email,
                "password": credentials.password
            })

            return{
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid login credentials"
            )
        


