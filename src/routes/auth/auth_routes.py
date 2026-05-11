from fastapi import APIRouter, Request
from firebase_admin import auth

router = APIRouter()


@router.post("/auth/custom-token")
async def get_custom_token(request: Request):
    uid = request.state.user.get("uid")
    custom_token = auth.create_custom_token(uid)
    return {"customToken": custom_token.decode()}
