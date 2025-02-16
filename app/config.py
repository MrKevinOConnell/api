from functools import lru_cache
from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    testing: bool = True
    profiling: bool = False
    cdn_url: str = "https://cdn.newshades.xyz"
    cdn_media_folder: str = "media"
    environment: str = "development"

    mongodb_url: str = "localhost:27017"
    mongodb_db: str = "newshades"
    mongodb_test_db: str = "newshades-test"

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_username: Optional[str]
    redis_password: Optional[str]

    jwt_secret_key: str
    jwt_access_token_expire_minutes: Optional[int] = 60
    jwt_refresh_token_expire_minutes: Optional[int] = 10080

    web3_provider_url_ws: Optional[str]

    pusher_app_id: Optional[str]
    pusher_key: Optional[str]
    pusher_secret: Optional[str]
    pusher_cluster: Optional[str]

    sentry_dsn: Optional[str]

    cloudflare_account_id: Optional[str]
    cloudflare_images_api_token: Optional[str]

    aws_access_key_id: Optional[str]
    aws_secret_access_key: Optional[str]
    aws_default_region: Optional[str]
    aws_media_bucket: str = "cdn.newshades.xyz"

    giphy_api_key: Optional[str]
    tenor_api_key: Optional[str]

    alchemy_api_key: Optional[str]

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
