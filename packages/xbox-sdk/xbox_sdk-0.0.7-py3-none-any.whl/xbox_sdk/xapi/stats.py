from ..lib.client import Client


class Stats:
    @classmethod
    def by_xuid(cls, xuid: str, title_id: str):
        response = Client.get(f'/{xuid}/game-stats/{title_id}')
        return response.json()
