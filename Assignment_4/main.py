
#import necessary libraries
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from supabase import create_client, Client
from fastapi import FastAPI,HTTPException, status,Request,Depends
from pydantic import BaseModel
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials





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
        

@app.get("/public/info")
def public_info():
    return{"message": "Welcome stranger! This info is public."}

security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
   token = credentials.credentials

   try:
        response = supabase.auth.get_user(token)
        return response.user
   
   except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )


@app.get("/protected/profile")
def protected_profile(user = Depends(get_current_user)):
    # The route body only runs if get_current_user succeeds
    return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at
    }


# 3. The Logout Route
@app.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(user = Depends(get_current_user)):
    # This is a protected route; you can only log out if you are verified
    supabase.auth.sign_out()
    return # 204 No Content expects no response body

# 4. Checkpoint Route
@app.get("/protected/dashboard")
def protected_dashboard(user = Depends(get_current_user)):
    # Reusing the exact same guard for a new room
    return {"message": f"Welcome to your private dashboard, {user.email}!"}    
