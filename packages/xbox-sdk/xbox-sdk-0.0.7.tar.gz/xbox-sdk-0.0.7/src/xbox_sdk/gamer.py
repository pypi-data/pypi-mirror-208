from .xapi import Profile, ProfileSpecific, Social, Stats, Content
from collections import defaultdict


class Gamer:
    @classmethod
    def by_xuid(cls, xuid: str):
        profile = Profile.by_xuid(xuid)
        return cls(
            xuid=profile['xuid'],
            gamertag=profile['gamertag'],
            gamer_score=profile['gamerScore'],
            gamer_picture_url=profile['displayPicRaw'],
            account_tier=profile['detail']['accountTier'],
            xbox_one_rep=profile['xboxOneRep'],
        )

    @classmethod
    def by_gamertag(cls, gamertag: str):
        profile = Profile.by_gamertag(gamertag)
        settings = defaultdict(lambda: None)
        for d in profile['settings']:
            settings[d['id']] = d['value']
        return cls(
            xuid=profile['id'],
            gamertag=settings['Gamertag'],
            gamer_score=settings['Gamerscore'],
            gamer_picture_url=settings['GameDisplayPicRaw'],
            account_tier=settings['AccountTier'],
            xbox_one_rep=settings['XboxOneRep'],
        )

    def __init__(
            self,
            xuid: str = None,
            gamertag: str = None,
            gamer_score: str = None,
            gamer_picture_url: str = None,
            account_tier: str = None,
            xbox_one_rep: str = None,
            **kwargs

    ):
        self.xuid = xuid
        self.gamertag = gamertag
        self.gamer_score = gamer_score
        self.gamer_picture_url = gamer_picture_url
        self.account_tier = account_tier
        self.xbox_one_rep = xbox_one_rep
        for k, v in kwargs.items():
            self.__dict__[k] = v

    def send_message(self, message: str) -> None:
        return ProfileSpecific.send_message(self.xuid, message)

    def add_friend(self):
        return ProfileSpecific.add_friend(self.xuid)

    def remove_friend(self):
        return ProfileSpecific.remove_friend(self.xuid)

    def friends(self):
        return Social.friends(self.xuid)

    def friends_playing_game(self, title_id: str):
        return Social.friends_playing_game(self.xuid, title_id)

    def stats(self, title_id: str):
        return Stats.by_xuid(self.xuid, title_id)

    def screenshots(self):
        return Content.screenshots(self.xuid)

    def screenshots_for_game(self, title_id: str):
        return Content.screenshots_for_game(self.xuid, title_id)

    def __repr__(self):
        gamertag = f"gamertag={repr(self.gamertag)}"
        xuid = f"xuid={repr(self.xuid)}"
        return f"<Gamer({gamertag}, {xuid})>"
