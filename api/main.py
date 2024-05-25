from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from controllers.UserController import user_controller_router
from utils.auth_utils import OktaJWTMiddleware
import os
from dotenv import load_dotenv

app = FastAPI()
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

tags_metadata = [
    {"name": "Users", "description": "Operations related to user management"}
]

# Include the routers from controller modules
app.include_router(user_controller_router, prefix="/users", tags=["Users"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Add Okta JWT Middleware
# app.add_middleware(OktaJWTMiddleware)

if __name__ == '__main__':
    print("Inside main block")
    uvicorn.run("main:app",host=os.environ.get("HOST"), port=os.environ.get("PORT"), reload=True)
