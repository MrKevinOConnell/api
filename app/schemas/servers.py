from datetime import datetime
from typing import Optional

from pydantic import Field

from app.schemas.base import APIBaseCreateSchema, APIBaseSchema, APIBaseUpdateSchema, PyObjectId


class ServerSchema(APIBaseSchema):
    name: str
    owner: PyObjectId = Field()

    class Config:
        schema_extra = {
            "example": {"id": "61e17018c3ee162141baf5c9", "name": "Verbs", "owner": "61e17018c3ee162141baf5c7"}
        }


class ServerCreateSchema(APIBaseCreateSchema):
    name: str


class ServerMemberSchema(APIBaseSchema):
    server: PyObjectId = Field()
    user: PyObjectId = Field()

    display_name: Optional[str] = Field()
    pfp: Optional[dict]
    joined_at: datetime

    class Config:
        schema_extra = {
            "example": {
                "id": "61e17018c3ee162141baf5c9",
                "server": "c3ee162141baf5c1",
                "user": "c3ee162141baf5c1",
                "display_name": "fun.eth",
                "pfp": {
                    "cf_id": "5adcdc13-0a45-45cd-0707-31eab9997c00",
                    "contract": "0x58f7e9810f5559dc759b731843212370363e433e",
                    "token_id": "100",
                    "token": {},
                    "verified": True,
                    "input": "https://opensea.io/assets/0x58f7e9810f5559dc759b731843212370363e433e/100",
                    "input_image_url": "https://cloudflare-ipfs.com/ipfs/.../image.png",
                },
                "joined_at": "2022-01-01T00:00:00+01:00",
            }
        }


class ServerMemberUpdateSchema(APIBaseUpdateSchema):
    display_name: Optional[str]
    pfp: Optional[str]
