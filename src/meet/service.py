from fastapi import Depends

from src.core.middlewares.error import ApiError
from src.core.database import SessionLocal, get_db

from .model import Meet, ObjectMeet
from .schema import CreateMeet, UpdateMeet

class MeetService:
    def __init__(self, db: SessionLocal = Depends(get_db)):
        self.db = db

    def create_meet(self, dto: CreateMeet):
        meet = Meet(
            name=dto.name,
            color=dto.color
        )

        self.db.add(meet)
        self.db.commit()
        self.db.refresh(meet)

        return meet
    
    def get_all(self):
        return self.db.query(Meet).all()
    
    def get_by_id(self, id):
        meet =  self.db.query(Meet).filter(Meet.id == id).first()
        if not meet:
            raise ApiError(message="Cannot  find this meet", error="Bad Request", status_code=400)
        return meet
    
    def get_objects(self, id):
        meet =  self.db.query(Meet).filter(Meet.id == id).first()
        if not meet:
            raise ApiError(message="Cannot  find this meet", error="Bad Request", status_code=400)
        return meet.object_meets
    
    def update(self, id, dto: UpdateMeet):
        meet =  self.db.query(Meet).filter(Meet.id == id).first()
        if not meet:
            raise ApiError(message="Cannot  find this meet", error="Bad Request", status_code=400)
        
        meet.name = dto.name
        meet.color = dto.color

        self.db.commit()
        
        self.db.query(ObjectMeet).filter(ObjectMeet.meet_id == id).delete()

        objects = [
            ObjectMeet(
                name=object_meet.name,
                x=object_meet.x,
                y=object_meet.y,
                z_index=object_meet.zindex,
                orientation=object_meet.orientation,
                meet_id=id
            ) for object_meet in dto.objects
        ]

        self.db.add_all(objects)
        self.db.commit()

        self.db.refresh(meet)

        return {
            **meet.__dict__,
            'objects': [object_meet.__dict__ for object_meet in meet.object_meets]
        }
    
    def delete(self, id):
        meet =  self.db.query(Meet).filter(Meet.id == id).first()
        if not meet:
            raise ApiError(message="Cannot  find this meet", error="Bad Request", status_code=400)
        
        self.db.delete(meet)
        self.db.commit()

        return meet

