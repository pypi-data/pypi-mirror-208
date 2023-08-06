from ..lib.client import Client


class Marketplace:
    @classmethod
    def featured_games(cls):
        response = Client.get(f'/marketplace/featured-games')
        return response.json()

    @classmethod
    def latest_games(cls):
        response = Client.get(f'/marketplace/latest-games')
        return response.json()

    @classmethod
    def search(cls, query: str):
        response = Client.get(f'/marketplace/query/{query}')
        return response.json()

    @classmethod
    def show(cls, id: str = None, title_id: str = None, product_id: str = None):
        if id is None and title_id is None and product_id is None:
            raise Exception("A marketplace product id must be provided.")
        response = Client.get(f'/marketplace/show/{id or title_id or product_id}')
        return response.json()

    @classmethod
    def most_played_games(cls):
        response = Client.get(f'/marketplace/most-played-games')
        return response.json()
