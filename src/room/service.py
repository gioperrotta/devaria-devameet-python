from fastapi import Depends
from src.core.middlewares.error import ApiError
from src.core.database import SessionLocal, get_db

from src.auth.model import User
from src.meet.model import Meet

from .model import Position
from .schema import ToggleMute, UpdatePosition


class RoomService:
    def __init__(self, db: SessionLocal = Depends(get_db)):
        self.db = db
    
    def __get_meet(self, link):
        meet = self.db.query(Meet).filter(Meet.link == link).one()
        if not meet:
            raise ApiError(message="Cannot  find this meet", error="Bad Request", status_code=400)
        
        return meet
    
    def __get_new_position(self,previus_orientation, x, y, new_orientation):
        if new_orientation == previus_orientation:
            if new_orientation == 'right' and x < 7:
                x = x + 1
            elif new_orientation == 'left' and x > 1:
                x = x - 1
            elif new_orientation == 'bottom' and y < 7:
                y = y + 1
            elif new_orientation == 'top' and y > 1:
                y = y - 1
        return x, y
   
    def get_room(self, link: str):
        meet = self.__get_meet(link)
        objects = meet.object_meets
        return {
            'link': link,
            'name': meet.name,
            'color': meet.color,
            'user_id': meet.user_id,
            'objects': objects
        }
    
    def list_users_position(self, link: str):
        meet = self.__get_meet(link)
        return self.db.query(Position).filter(Position.meet_id == meet.id).all()
    
    def delete_users_position(self, client_id: str):
        self.db.query(Position).filter(Position.client_id == client_id).delete()
        self.db.commit()
    
    def get_user_position(self, client_id: str):
        return self.db.query(Position).filter(Position.client_id == client_id).first()

    def update_user_position_only_orientation(self, user_id, link, client_id, orientation):
        meet = self.__get_meet(link)
        user = self.db.query(User).filter(User.id == user_id).first()
        previus_position_user = self.db.query(Position).filter(Position.client_id == client_id).one()

        x, y = self.__get_new_position(previus_position_user.orientation, previus_position_user.x, previus_position_user.y, orientation)
       
        self.db.query(Position)\
                .filter(Position.meet_id == meet.id)\
                .filter(Position.user_id == user.id)\
                .update({
                'x': x,
                'y': y,
                'orientation': orientation
            })

        self.db.commit()

    def update_user_position(self, user_id, link, client_id, dto: UpdatePosition):
        meet = self.__get_meet(link)
        user = self.db.query(User).filter(User.id == user_id).first()
    
        position = Position(
            x=dto.x,
            y=dto.y,
            orientation=dto.orientation,
            user_id=user.id,
            meet_id=meet.id,
            client_id=client_id,
            name=user.name,
            avatar=user.avatar
        )

        users_in_room = self.db.query(Position).filter(Position.meet_id == meet.id).all()

        if any(user for user in users_in_room if user.user_id == user.id or user.client_id == client_id):
            position = self.db.query(Position).filter(Position.client_id == client_id).one()
            position.x = dto.x
            position.y = dto.y
            position.orientation = dto.orientation
        elif len(users_in_room) > 20:
            raise ApiError(message='Meet is full', error='UpdateMeerError', status_code=400)
        else:
            self.db.add(position)

        self.db.commit()

    def update_user_mute(self, sid, dto: ToggleMute):
        meet = self.__get_meet(dto.link)
        user = self.db.query(User).filter(User.id == dto.user_id).first()
       
        position = self.db.query(Position).filter(Position.client_id == sid).one()
        send_user = position.user_id
        room_owner_user = meet.user_id
        if send_user == user.id or room_owner_user == send_user:
            self.db.query(Position)\
                .filter(Position.meet_id == meet.id)\
                .filter(Position.user_id == user.id)\
                .update({
                'muted': dto.muted
            })

        self.db.commit()

    