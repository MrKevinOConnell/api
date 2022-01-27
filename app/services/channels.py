import http
from datetime import timezone
from typing import Union

from bson import ObjectId
from fastapi import HTTPException

from app.models.base import APIDocument
from app.models.channel import Channel, ChannelReadState
from app.models.message import Message
from app.models.user import User
from app.schemas.channels import ChannelReadStateCreateSchema, DMChannelCreateSchema, ServerChannelCreateSchema
from app.services.crud import create_item, delete_item, get_item, get_item_by_id, get_items, update_item


async def create_dm_channel(channel_model: DMChannelCreateSchema, current_user: User) -> Union[Channel, APIDocument]:
    current_user_id = str(current_user.id)
    if current_user_id not in channel_model.members:
        channel_model.members.insert(0, current_user_id)

    # if same exact dm channel already exists, ignore
    filters = {
        "owner": current_user.id,
        "members": {"$all": [ObjectId(member) for member in channel_model.members]},
    }
    existing_dm_channels = await get_items(filters=filters, result_obj=Channel, current_user=current_user)
    if existing_dm_channels:
        # TODO: return 200 status code
        return existing_dm_channels[0]

    return await create_item(channel_model, result_obj=Channel, current_user=current_user, user_field="owner")


async def create_server_channel(
    channel_model: ServerChannelCreateSchema, current_user: User
) -> Union[Channel, APIDocument]:
    return await create_item(channel_model, result_obj=Channel, current_user=current_user, user_field="owner")


async def create_channel(
    channel_model: Union[DMChannelCreateSchema, ServerChannelCreateSchema], current_user: User
) -> Union[Channel, APIDocument]:
    kind = channel_model.kind
    if kind == "dm":
        return await create_dm_channel(channel_model, current_user)
    elif kind == "server":
        return await create_server_channel(channel_model, current_user)
    else:
        raise Exception(f"unexpected channel kind: {kind}")


async def get_server_channels(server_id, current_user: User) -> [Channel]:
    return await get_items(filters={"server": ObjectId(server_id)}, result_obj=Channel, current_user=current_user)


async def get_dm_channels(current_user: User) -> [Channel]:
    return await get_items(filters={"members": current_user.pk}, result_obj=Channel, current_user=current_user)


async def delete_channel(channel_id, current_user: User):
    channel = await get_item_by_id(id_=channel_id, result_obj=Channel, current_user=current_user)
    channel_owner = channel.owner
    is_channel_owner = channel_owner == current_user

    if channel.kind == "server":
        server = await channel.server.fetch()
        server_owner = server.owner
        if not is_channel_owner or not current_user == server_owner:
            raise HTTPException(status_code=http.HTTPStatus.FORBIDDEN)
    elif channel.kind == "dm":
        raise HTTPException(status_code=http.HTTPStatus.FORBIDDEN)
    else:
        raise Exception(f"unexpected kind of channel: {channel.kind}")

    return await delete_item(item=channel)


async def update_channel_last_message(channel_id, message: Union[Message, APIDocument], current_user: User):
    channel = await get_item_by_id(id_=channel_id, result_obj=Channel, current_user=current_user)
    message_ts = message.created_at.replace(tzinfo=timezone.utc).timestamp()
    if not channel.last_message_ts or message_ts > channel.last_message_ts:
        await update_item(item=channel, data={"last_message_ts": message_ts}, current_user=current_user)


async def update_channel_read_state(user_id: str, channel_id: str, last_read_ts: float):
    user = await get_item_by_id(id_=user_id, result_obj=User)
    channel = await get_item_by_id(id_=channel_id, result_obj=Channel)

    if isinstance(last_read_ts, int):
        # JS timestamps are diff format than Python
        last_read_ts = last_read_ts / 1000

    read_state_model = ChannelReadStateCreateSchema(channel=str(channel.id), last_read_ts=last_read_ts)

    read_state = await get_item(filters={"user": user, "channel": channel}, result_obj=ChannelReadState)
    if not read_state:
        await create_item(read_state_model, result_obj=ChannelReadState, current_user=user)
    else:
        read_state = await update_item(item=read_state, data={"last_read_ts": last_read_ts})

    return read_state
