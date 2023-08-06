from ..lib.client import Client


class Social:
    @classmethod
    def friends(cls, xuid: str):
        response = Client.get(f'/{xuid}/friends')
        return response.json()

    @classmethod
    def friends_playing_game(cls, xuid: str, title_id: str):
        response = Client.get(f'/{xuid}/friends-playing/{title_id}')
        return response.json()

    @classmethod
    def xbox_sponsored_activities(cls):
        response = Client.get(f'/xbox-activity-feed')
        return response.json()

