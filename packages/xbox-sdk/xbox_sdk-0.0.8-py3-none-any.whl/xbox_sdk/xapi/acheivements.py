from ..lib.client import Client


class Achievements:
    @classmethod
    def list(cls, xuid: str):
        response = Client.get(f'/{xuid}/titlehub-achievement-list')
        return response.json()

    @classmethod
    def xbox_one(cls, xuid: str, title_id: str):
        response = Client.get(f'/{xuid}/achievements-alt/{title_id}')
        return response.json()

    @classmethod
    def by_game(cls, xuid: str, title_id: str):
        response = Client.get(f'/{xuid}/achievements/{title_id}')
        return response.json()
