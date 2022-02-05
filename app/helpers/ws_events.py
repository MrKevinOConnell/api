from enum import Enum


class WebSocketServerEvent(Enum):
    CONNECTION_READY = "CONNECTION_READY"

    MESSAGE_CREATE = "MESSAGE_CREATE"
    MESSAGE_REMOVE = "MESSAGE_REMOVE"
    MESSAGE_UPDATE = "MESSAGE_UPDATE"

    MESSAGE_REACTION_ADD = "MESSAGE_REACTION_ADD"
    MESSAGE_REACTION_REMOVE = "MESSAGE_REACTION_REMOVE"

    CHANNEL_READ = "CHANNEL_READ"