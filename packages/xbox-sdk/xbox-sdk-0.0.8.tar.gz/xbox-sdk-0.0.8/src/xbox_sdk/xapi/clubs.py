from ..lib.client import Client


class Clubs:
    @classmethod
    def details(cls, club_id: str):
        response = Client.get(f'/clubs/details/{club_id}')
        return response.json()

    @classmethod
    def owned(cls):
        response = Client.get(f'/clubs/owned')
        return response.json()

    @classmethod
    def by_xuid(cls, xuid: str):
        response = Client.get(f'/clubs/joined/{xuid}')
        return response.json()

    @classmethod
    def by_name(cls, name: str):
        response = Client.get(f'/clubs/search/name/{name}')
        return response.json()

    @classmethod
    def by_tags(cls, *tags: str):
        response = Client.get(f'/clubs/search/tags/{",".join(tags)}')
        return response.json()

    @classmethod
    def by_titles(cls, *titles: str):
        response = Client.get(f'/clubs/search/titles/{",".join(titles)}')
        return response.json()
