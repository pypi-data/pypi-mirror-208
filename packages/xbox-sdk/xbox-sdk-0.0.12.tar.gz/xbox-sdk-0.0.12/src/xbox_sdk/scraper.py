from xbox_sdk.client import Client
from xbox_sdk.user import User
import json
from pathlib import Path

class XboxScraper:
    def __init__(self, root_player: User, game_title_id=983730484):
        self.__client = Client()
        self.__client.timeout = 10
        self.preferred_game_title = game_title_id
        self.relevant_friends = []
        self.root_player = root_player

    def inspect_friend(self, gamer_tag: str, xuid: str):
        assert isinstance(gamer_tag, str)
        assert isinstance(xuid, str)
        user = User(gamer_tag, xuid, self.__client)
        if not user.is_valid():
            self.save_last_positions()
            user.delete_file()
        if self.is_friend_relevant(user):
            self.relevant_friends.append(user)
            self.save_relevant_friend(user)
        self.save_seen_friend(user)

    def is_friend_relevant(self, user: User):
        seen = self.load_seen_friends()
        if user.gamer_tag in seen:
            return False
        return True

    def friends_playing_title(self, user: User):
        playing = user.friends_playing_title()
        if 'people' not in playing:
            return []

        friends_list = []
        people = playing['people']
        for person in people:
            gamer_tag = ''
            if 'gamertag' in person:
                gamer_tag = person['gamertag']
            elif 'displayName' in person:
                gamer_tag = person['displayNme']
            elif 'modernGamertag' in person:
                gamer_tag = person['modernGamertag']
            else:
                continue
            friends_list.append([gamer_tag, person['xuid']])
        return friends_list


    def save_relevant_friend(self, user: User):
        print("Saving Relevant Friend: {}".format(user.gamer_tag))
        data = {}
        dir = Path("xbox/blueprint_data/relevant_friends.json")
        if dir.exists():
            with open(dir, 'r') as r:
                data = json.load(r)
        data.update({user.gamer_tag: user.xuid})
        with open(dir, 'w') as w:
            json.dump(data, w)

    def save_last_positions(self):
        dir = Path("xbox/blueprint_data/backup.json")
        positions = []
        for user in self.relevant_friends:
            positions.append([user.gamer_tag, str(user.xuid)])
        with open(dir, 'w') as w:
            json.dump(positions, w)

    def save_seen_friend(self, user: User):
        data = {}
        dir = Path("xbox/blueprint_data/seen_friends.json")
        if dir.exists():
            with open(dir, 'r') as r:
                data = json.load(r)
        data.update({user.gamer_tag: user.xuid})
        with open(dir, 'w') as w:
            json.dump(data, w)

    def save_error_friend(self, error_data):
        data = []
        dir = Path("xbox/blueprint_data/error_friend.json")
        if dir.exists():
            with open(dir, 'r') as r:
                data = json.load(r)
        data.append(error_data)
        with open(dir, 'w') as w:
            json.dump(data, w)

    def load_seen_friends(self):
        dir = Path("xbox/blueprint_data/seen_friends.json")
        if not dir.exists():
            return {}
        with open(dir, 'r') as r:
            return json.load(r)

    def load_last_positions(self):
        dir = Path("xbox/blueprint_data/backup.json")
        positions = []
        if not dir.exists():
            return positions
        with open(dir, 'r') as r:
            positions = json.load(r)
        for gamer_tag, xuid in positions:
            self.relevant_friends.append(User(gamer_tag, xuid, self.__client))
        return self.relevant_friends

    def load_relevant_list(self):
        dir = Path("xbox/blueprint_data/relevant_friends.json")
        if not dir.exists():
            return {}
        with open(dir, 'r') as r:
            return json.load(r)

    def run(self):
        last_positions = self.load_last_positions()
        queue = [self.root_player] + last_positions
        while len(queue) > 0:
            user = queue.pop()
            for gamer_tag, xuid in self.friends_playing_title(user):
                if gamer_tag is None or xuid is None:
                    continue
                self.inspect_friend(gamer_tag, str(xuid))

            for friend in self.relevant_friends:
                queue.append(friend)
                self.relevant_friends.clear()
            del user



    def __del__(self):
        self.save_last_positions()


