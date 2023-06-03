from fastapi import APIRouter, Depends

from src.auth.handler import get_current_user

from .service import RoomService

router = APIRouter()
    
@router.get('/{link}')
async def get_room(
    link: str, 
    username: str = Depends(get_current_user),
    service: RoomService = Depends(RoomService) 
  ):
    return service.get_room(link)