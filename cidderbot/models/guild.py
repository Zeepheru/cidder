from typing import List

# UNUSED


# Unkown whether these models are needed. Not used for the time being.
class CidderGuild:
    def __init__(self, guild_id: int, guild_name: str, channel_ids: List[int]) -> None:
        self._id = guild_id
        self._name = guild_name
        self._channels = [CidderChannel(self, channel_id) for channel_id in channel_ids]

    def __repr__(self) -> str:
        return f"<Guild {self._id} ({self._name})>"

    def __str__(self) -> str:
        return f"<Guild {self._id} ({self._name})>"

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name


class CidderChannel:
    def __init__(self, guild: CidderGuild, channel_id: int) -> None:
        self._id = channel_id
        self._guild = guild

    def __repr__(self) -> str:
        return f"<Channel {self._id}>"

    def __str__(self) -> str:
        return f"<Channel {self._id} in {self._guild}>"

    @property
    def id(self):
        return self._id
