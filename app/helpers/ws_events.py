from enum import Enum


class WebSocketServerEvent(Enum):
    CONNECTION_READY = "CONNECTION_READY"

    MESSAGE_CREATE = "MESSAGE_CREATE"
    MESSAGE_REMOVE = "MESSAGE_REMOVE"
    MESSAGE_UPDATE = "MESSAGE_UPDATE"
    MESSAGE_REACTION_ADD = "MESSAGE_REACTION_ADD"
    MESSAGE_REACTION_REMOVE = "MESSAGE_REACTION_REMOVE"

    CHANNEL_READ = "CHANNEL_READ"

    USER_PROFILE_UPDATE = "USER_PROFILE_UPDATE"
    USER_PRESENCE_UPDATE = "USER_PRESENCE_UPDATE"
    USER_TYPING = "USER_TYPING"

    SERVER_PROFILE_UPDATE = "SERVER_PROFILE_UPDATE"
    SERVER_USER_JOINED = "SERVER_USER_JOINED"
    SERVER_UPDATE = "SERVER_UPDATE"

    NOTIFY_USER_MENTION = "NOTIFY_USER_MENTION"
