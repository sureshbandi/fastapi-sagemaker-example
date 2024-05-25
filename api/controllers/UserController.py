from fastapi import HTTPException, Depends, Header
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter

user_controller_router = InferringRouter()

@cbv(user_controller_router)
class UserController:

    @user_controller_router.get("/data")
    def get_data(self):
        return {"message": "Hello World"}
    
   
