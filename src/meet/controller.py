from fastapi import APIRouter, Body, Depends

from src.auth.handler import get_current_user

from .schema import CreateMeet, UpdateMeet
from .service import MeetService


router = APIRouter()

@router.get('/')
async def get_all(
    username: str = Depends(get_current_user),
    service: MeetService = Depends(MeetService) 
  ):
  return service.get_all()

@router.get('/{id}')
async def get_by_id(
    id: int,
    username: str = Depends(get_current_user),
    service: MeetService = Depends(MeetService) 
  ):
  return service.get_by_id(id)

@router.post('/')
async def create_meet(
    dto: CreateMeet, 
    # username: str = Depends(get_current_user),
    user: str = Depends(get_current_user),
    service: MeetService = Depends(MeetService) 
  ):
  print('username = ',  user, 'dto =', dto)
  return service.create_meet(user, dto)

@router.put('/{id}')
async def update_meet(
    id: str, 
    dto: UpdateMeet = Body(embed=False), 
    username: str = Depends(get_current_user), 
    service: MeetService = Depends(MeetService)
  ):
  return service.update(id, dto)

@router.delete('/{id}')
async def delete_meet(
    id: str, 
    username: str = Depends(get_current_user), 
    service: MeetService = Depends(MeetService)
  ):
  return service.delete(id)

@router.get('/{id}/object')
async def get_objects(
    id: int,
    username: str = Depends(get_current_user),
    service: MeetService = Depends(MeetService) 
  ):
  return service.get_objects(id)