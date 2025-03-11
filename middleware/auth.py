from fastapi import Request
from main import app

@app.middleware('http')
async def authMiddleware(request: Request, next_call):
  #before code
  next_call()
  # after code