import json
from pathlib import Path
from time import sleep


class User:
    def __init__(self, gamer_tag='ensue9805', xuid='2535434466564225', client=None):
        assert isinstance(gamer_tag, str)
        assert isinstance(xuid, str)
        self.gamer_tag = gamer_tag
        self.xuid = xuid
        self.data = {'gamer_tag': gamer_tag, 'xuid': xuid}
        self.gamer = client.gamer(gamer_tag, xuid)
        self.client = client
        self.client.timeout = 10
        self.__str = None
        self.save()

    def __api_get(self, url_path):
        return json.loads(self.client.api_get(url_path).text)

    def __is_cached(self):
        dir = Path("xbox/blueprint_data/xuid_{}.json".format(self.xuid))
        return dir.exists()

    def send_message(self, message):
        if len(message) > 255:
            raise OverflowError("Message exceeded the 255 character maximum")
        print("Sending to: {}\t".format(self.gamer_tag), end='')
        try:
            gamer = self.client.gamer(self.gamer_tag, self.xuid)
            result = gamer.send_message(message=message)
            if not result.ok:
                print('\033[91m' + 'FAILED' + '\033[0m')
                return False
            print('\033[92m' + "SUCCESS" + '\033[0m')
            return True
        except Exception as e:
            print('\033[91m' + 'FAILED: {}'.format(e) + '\033[0m')
            return False

    def profile(self):
        if self.__is_cached():
            data = self.load()
            return data[self.gamer_tag]['profile']
        try:
            return self.__api_get('{}/new-profile'.format(self.xuid))
        except Exception:
            try:
                return self.gamer.get('profile')
            except Exception:
                return {"error_code": "forbidden"}

    def friends(self):
        if self.__is_cached():
            data = self.load()
            return data[self.gamer_tag]['friends']
        try:
            return self.__api_get("{}/friends".format(self.xuid))
        except Exception:
            try:
                return self.gamer.get('friends')
            except Exception:
                return {"error_code": "forbidden"}

    def gamercard(self):
        if self.__is_cached():
            data = self.load()
            return data[self.gamer_tag]['gamercard']
        try:
            return self.__api_get("{}/gamercard".format(self.xuid))
        except Exception:
            try:
                return self.gamer.get('gamercard')
            except Exception:
                return {"error_code": "forbidden"}

    def presence(self):
        try:
            return self.__api_get("{}/presence".format(self.xuid))
        except Exception:
            try:
                return self.gamer.get('presence')
            except Exception:
                return {"error_code": "forbidden"}

    def followers(self):
        if self.__is_cached():
            data = self.load()
            return data[self.gamer_tag]['followers']
        try:
            return self.__api_get("{}/followers".format(self.xuid))
        except Exception:
            try:
                return self.gamer.get('followers')
            except Exception:
                return {"error_code": "forbidden"}

    def friends_playing_title(self, title_id=983730484):
        if self.__is_cached():
            data = self.load()
            return data[self.gamer_tag]['friends_playing_title']
        try:
            return self.__api_get("{}/friends-playing/{}".format(self.xuid, title_id))
        except Exception:
            try:
                return self.gamer.get('friends-playing', str(title_id))
            except Exception:
                return {"error_code": "forbidden"}

    def game_stats(self, title_id=983730484):
        """ Can get Ark Statistics: kills, deaths, and number creatures tamed """
        """
        for property in game_stats['groups'][0]['statlistscollection'][0]['stats']:
            number = property['groupproperties']['Ordinal']
            stat_name = property['groupproperties']['DisplayName']
            print("{}: {}".format(stat_name, number))
        """
        if self.__is_cached():
            data = self.load()
            return data[self.gamer_tag]['game_stats']
        try:
            return self.__api_get("{}/game-stats/{}".format(self.xuid, title_id))
        except Exception:
            try:
                return self.gamer.get("game-stats", str(title_id))
            except Exception:
                return {"error_code": "forbidden"}

    def xboxone_games(self):
        if self.__is_cached():
            data = self.load()
            return data[self.gamer_tag]['xboxone_games']
        try:
            return self.__api_get("{}/xboxonegames".format(self.xuid))
        except Exception:
            try:
                return self.gamer.get('xboxonegames')
            except Exception:
                return {"error_code": "forbidden"}

    def titlehub_achievement_list(self):
        """ Gets all games last time played, achievements, and gamerscore """
        """
        for title in titlehub_achievementlist['titles']:
            print(title['name'])
            print(title['achievement'])
            print(title['titleHistory'])
        """
        if self.__is_cached():
            data = self.load()
            return data[self.gamer_tag]['titlehub_achievement_list']
        try:
            return self.__api_get("{}/titlehub-achievement-list".format(self.xuid))
        except Exception:
            try:
                return self.gamer.get('titlehub-achievement-list')
            except Exception:
                return {"error_code": "forbidden"}

    def __str__(self):
        if self.__str is not None:
            return self.__str
        if self.__is_cached():
            return str(self.load())
        limit = self.client.calls_remaining()
        if int(limit['X-RateLimit-Remaining']) == 0:
            seconds = int(limit['X-RateLimit-Reset'])
            while seconds > 0:
                print("[Limit Exceeded] Time Until Reset: {:02d}:{:02d}".format(seconds // 60, seconds % 60))
                sleep(5)
                seconds -= 5

        profile = json.dumps(self.profile())
        s = '{' + '"{}"'.format(self.gamer_tag) + ': {' + '"xuid": {}, '.format(self.xuid)
        s += '"profile": {}, '.format(self.xuid, profile)
        gamercard = json.dumps(self.gamercard())
        s += '"gamercard": {}, '.format(gamercard)
        friends_playing_title = json.dumps(self.friends_playing_title())
        s += '"friends_playing_title": {}, '.format(friends_playing_title)
        titlehub_achievement_list = json.dumps(self.titlehub_achievement_list())
        s += '"titlehub_achievement_list": {}'.format(titlehub_achievement_list)
        s += '}}'
        self.__str = s
        return s

    def save(self):
        if not self.__is_cached() and self.is_valid():
            str_data = str(self)
            data = json.loads(str_data)
            dir = Path("xbox/data/xuid_{}.json".format(self.xuid))
            with open(dir, 'w') as w:
                json.dump(data, w)

    def delete_file(self):
        if self.__is_cached():
            dir = Path("xbox/data/xuid_{}.json".format(self.xuid))
            dir.unlink()

    def load(self):
        if self.__is_cached():
            dir = Path("xbox/data/xuid_{}.json".format(self.xuid))
            with open(dir, 'r') as r:
                return json.load(r)
        return None

    def is_valid(self):
        if self.__is_cached():
            data = self.load()[self.gamer_tag]
        else:
            str_data = str(self)
            data = json.loads(str_data)[self.gamer_tag]
        if isinstance(data['profile'], dict) and "error_code" in data['profile']:
            return False
        if isinstance(data['gamercard'], dict) and "error_code" in data['gamercard']:
            return False
        if isinstance(data['friends_playing_title'], dict) and "error_code" in data['friends_playing_title']:
            return False
        if isinstance(data['titlehub_achievement_list'], dict) and "error_code" in data['titlehub_achievement_list']:
            return False
        return True

    def __repr__(self):
        return "<XboxUser(gamer_tag: {}, xuid: {})>".format(self.gamer_tag, self.xuid)

    def __del__(self):
        self.save()
