from fastapi import FastAPI
from fastapi_socketio import SocketManager
from src.core.logger import ApiLogger

from src.core.database import SessionLocal
from .schema import UpdatePosition, ToggleMute
from .service import RoomService

logger  = ApiLogger(__name__)

class WebSocketObject:
    def __init__(self, sid: str, link: str, user_id: str):
        self.sid = sid
        self.link = link
        self.user_id = user_id
class WebSocketServer:
    def __init__(self, app: FastAPI, origins: list | str = '*'):
        logger.info("Socket server initialized")
        self.app = app
        self.socket_manager = SocketManager(app=app, cors_allowed_origins=origins, mount_location='/')
        self.active_sockets: list[WebSocketObject] = []
        self.run()

    def run(self):
        self.socket_manager.on('disconnect', self.on_disconnect)
        self.socket_manager.on('join', self.on_join)
        self.socket_manager.on('move', self.on_move)
        self.socket_manager.on('move-only-orientation', self.on_move_only_orientation)
        self.socket_manager.on('toggl-mute-user', self.on_toggl_mute_user)
        self.socket_manager.on('call-user', self.on_call_user)
        self.socket_manager.on('make-answer', self.on_make_answer)

    async def on_disconnect(self, sid):
        logger.info('on_disconnect method called')

        user_socket = list(filter(lambda u: u.sid == sid, self.active_sockets))
     
        self.active_sockets = list(filter(lambda u: u.sid != sid, self.active_sockets))

        if len(user_socket) == 0:
            return

        user_socket = user_socket[0]

        with SessionLocal() as db_connection:
            service = RoomService(db_connection)
            service.delete_users_position(sid)

        await self.socket_manager.emit(
            f'{user_socket.link}-remove-user', 
            {'socketId': sid}, 
            skip_sid=sid
          )
  
    async def on_join(self, sid, data):
        logger.info('on_join method called')
        link, user_id = data['link'], data['userId']
        existing_socket = [u for u in self.active_sockets
                           if u.user_id == user_id
                           and u.link == link]
        if len(existing_socket) == 0:
            logger.debug(f'on_join: adding user in room: socket={user_id}')
            self.active_sockets.append(WebSocketObject(sid, link, user_id))

            dto = UpdatePosition(x=2, y=2, orientation='bottom')

            with SessionLocal() as db_connection:
                service = RoomService(db_connection)
                service.update_user_position(user_id=user_id, link=link, client_id=sid, dto=dto)
                users = service.list_users_position(link)

            await self.socket_manager.emit(f'{link}-update-user-list', {'users': [user.to_json() for user in users]})
            await self.socket_manager.emit(f'{link}-add-user', {'user': sid}, skip_sid=sid)
        else:
            user = existing_socket[0]
            logger.debug(f'on_join:User already in room: socket={user}')
    
    async def on_move_old(self, sid, data):
        logger.debug(f'on_move method called')
        
        link = data['link']
        user_id = data['userId']
        x = data['x']
        y = data['y'] 
        orientation = data['orientation']

        dto = UpdatePosition(x=x, y=y, orientation=orientation)

        with SessionLocal() as db_connection:
            service = RoomService(db_connection)
            service.update_user_position(user_id=user_id, link=link, client_id=sid, dto=dto)
            users = service.list_users_position(link)

        await self.socket_manager.emit(f'{link}-update-user-list', {'users': [user.to_json() for user in users]})

    async def on_move_only_orientation(self, sid, data):
        logger.info(f'on_move method called')

        link = data['link']
        user_id = data['userId']

        with SessionLocal() as db_connection:
            service = RoomService(db_connection)
            service.update_user_position_only_orientation(user_id=user_id, link=link, client_id=sid, orientation=data['orientation'])
            users = service.list_users_position(link)

        await self.socket_manager.emit(f'{link}-update-user-list', {'users': [user.to_json() for user in users]})
    
    async def on_toggl_mute_user(self, sid, data):
        logger.debug(f'on_toggl_mute_user method called')
         
        link = data['link']
        user_id = data['userId']
        muted = data['muted']

        dto = ToggleMute(
            user_id=user_id,
            muted=muted,
            link=link
        )

        with SessionLocal() as db_connection:
            service = RoomService(db_connection)
            service.update_user_mute(sid, dto)
            users = service.list_users_position(link)

        await self.socket_manager.emit(f'{link}-update-user-list', {'users': [user.to_json() for user in users]})

    
    async def on_call_user(self, sid, data):
        logger.debug(f'on_call_user method called')
        offer, to = data['offer'], data['to']
        call_made_dto = {
            'offer':offer,
            'socket': sid
        }
        await self.socket_manager.emit('call-made', call_made_dto, to=to)
    
    async def on_make_answer(self, sid, data):
        logger.debug(f'on_make_answer method called')
        answer, to = data['answer'], data['to']
        make_answer_dto = {
            'answer':answer,
            'socket': sid
        }
        await self.socket_manager.emit('answer-made', make_answer_dto, to=to)

