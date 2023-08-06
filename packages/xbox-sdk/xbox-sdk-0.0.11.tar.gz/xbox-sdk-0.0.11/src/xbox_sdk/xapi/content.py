from ..lib.client import Client


class Content:
    @classmethod
    def screenshots_for_game(cls, xuid: str, title_id: str):
        response = Client.get(f'/{xuid}/screenshots/{title_id}')
        return response.json()

    @classmethod
    def screenshots(cls, xuid: str):
        response = Client.get(f'/{xuid}/screenshots')
        return response.json()

    @classmethod
    def gameclips_for_game(cls, xuid: str, title_id: str):
        response = Client.get(f'/{xuid}/game-clips/{title_id}')
        return response.json()

    @classmethod
    def gameclips(cls, xuid: str):
        response = Client.get(f'/{xuid}/game-clips')
        return response.json()
