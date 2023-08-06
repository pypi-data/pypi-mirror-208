from ..lib.client import Client


class Profile:
    @classmethod
    def by_gamertag(cls, gamertag: str):
        response = Client.get(f'/{gamertag}/profile-for-gamertag')
        return response.json()

    @classmethod
    def by_xuid(cls, xuid: str):
        response = Client.get(f'/{xuid}/profile')
        return response.json()

    @classmethod
    def activity(cls, xuid: str):
        response = Client.get(f'/{xuid}/activity')
        return response.json()

    @classmethod
    def gamercard(cls, xuid: str):
        response = Client.get(f'/{xuid}/gamercard')
        return response.json()

    @classmethod
    def presence(cls, xuid: str):
        response = Client.get(f'/{xuid}/presence')
        return response.json()

    @classmethod
    def title_history(cls, xuid: str):
        response = Client.get(f'/{xuid}/title-history')
        return response.json()

    @classmethod
    def xbox_one_games(cls, xuid: str):
        response = Client.get(f'/{xuid}/xboxonegames')
        return response.json()
