from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from fastapi import Request, Response

from src.core.database import SessionLocal

class DatabaseSessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        response = Response('Internal Server Error', status_code=500)
        try:
            request.state.db = SessionLocal() 
            response = await  call_next(request)    
        finally:
            request.state.db.close()
        return response
