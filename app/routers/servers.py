import http
from typing import List

from fastapi import APIRouter, Body, Depends

from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.servers import ServerCreateSchema, ServerMemberSchema, ServerSchema
from app.services.servers import create_server, get_server_members, get_servers, join_server

router = APIRouter()


@router.get("", summary="List servers", response_model=List[ServerSchema])
async def get_list_servers(current_user: User = Depends(get_current_user)):
    return await get_servers(current_user=current_user)


@router.post(
    "", response_description="Create new server", response_model=ServerSchema, status_code=http.HTTPStatus.CREATED
)
async def post_create_server(server: ServerCreateSchema = Body(...), current_user: User = Depends(get_current_user)):
    return await create_server(server, current_user=current_user)


@router.get(
    "/{server_id}/members",
    response_description="List server members",
    response_model=List[ServerMemberSchema],
    status_code=http.HTTPStatus.OK,
)
async def get_list_server_members(server_id, current_user: User = Depends(get_current_user)):
    return await get_server_members(server_id, current_user=current_user)


@router.post(
    "/{server_id}/join", summary="Join server", response_model=ServerMemberSchema, status_code=http.HTTPStatus.CREATED
)
async def post_join_server(server_id, current_user: User = Depends(get_current_user)):
    return await join_server(server_id=server_id, current_user=current_user)
