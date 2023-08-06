from ..lib.client import Client


class ProfileSpecific:

    @classmethod
    def conversation_details(cls, xuid: str):
        response = Client.get(f'/conversations/{xuid}')
        return response.json()

    @classmethod
    def conversations(cls):
        response = Client.get(f'/conversations')
        return response.json()

    @classmethod
    def messages(cls):
        response = Client.get(f'/messages')
        return response.json()

    @classmethod
    def profile(cls):
        response = Client.get(f'/profile')
        return response.json()

    @classmethod
    def activity_feed(cls):
        response = Client.get(f'/activity-feed')
        return response.json()

    @classmethod
    def add_friend(cls, xuid: str):
        response = Client.get(f'/{xuid}/add-as-friend')
        return response.json()

    @classmethod
    def remove_conversation(cls, xuid: str):
        response = Client.get(f'/conversation/{xuid}')
        return response.json()

    @classmethod
    def followers(cls):
        response = Client.get(f'/followers')
        return response.json()

    @classmethod
    def add_activity(cls, message: str):
        data = {'text': message}
        response = Client.post(f'/activity-feed', data=data)
        return response.json()

    @classmethod
    def recent_players(cls):
        response = Client.get(f'/recent-players')
        return response.json()

    @classmethod
    def remove_friend(cls, xuid: str):
        response = Client.get(f'/{xuid}/remove-friend')
        return response.json()

    @classmethod
    def send_message(cls, xuid: str, message: str):
        data = {'to': [xuid], "message": message}
        response = Client.post(f'/messages', data=data)
        return response.json()
