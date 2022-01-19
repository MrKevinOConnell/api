from typing import Optional, Type, Union

from bson import ObjectId
from umongo.document import DocumentImplementation

from app.models.base import APIDocument
from app.models.user import User
from app.schemas.base import APIBaseCreateSchema


async def create_item(
    item: APIBaseCreateSchema, result_obj: Type[APIDocument], current_user: User, user_field: Optional[str] = "user"
) -> APIDocument:
    db_object = result_obj(**item.dict())
    if user_field:
        db_object[user_field] = current_user
    await db_object.commit()
    return db_object


async def get_item_by_id(id_: str, result_obj: Type[APIDocument], current_user: User) -> APIDocument:
    item = await result_obj.find_one({"_id": ObjectId(id_)})
    return item


async def get_items(filters: dict, result_obj: Type[APIDocument], current_user: User) -> [APIDocument]:
    # TODO: add paging default size to settings
    items = await result_obj.find(filters).to_list(10)
    return items


async def get_item(filters: dict, result_obj: Type[APIDocument], current_user: User) -> APIDocument:
    item = await result_obj.find_one(filters)
    return item
