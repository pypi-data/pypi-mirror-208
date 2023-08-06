from .api_request import RequestAPI
from cakesAPI.models.cake import Cake
from cakesAPI.models.recipe import Recipe


class CakeAPI:
    def __init__(self, api_key):
        self.request = RequestAPI(api_key)

    def get_cakes_list(self):
        url = "https://the-birthday-cake-db.p.rapidapi.com/"
        response = self.request.send_request(url)

        cakes = []
        for cake_data in response:
            id = cake_data["id"]
            title = cake_data["title"]
            difficulty = cake_data["difficulty"]
            image = cake_data["image"]
            cake = Cake(id, title, difficulty, image)
            cakes.append(cake)

        return cakes

    def get_recipe_by_id(self, id):
        url = f"https://the-birthday-cake-db.p.rapidapi.com/{id}"
        response = self.request.send_request(url)

        recipe = Recipe(
            id=response['id'],
            title=response['title'],
            difficulty=response['difficulty'],
            portion=response['portion'],
            time=response['time'],
            description=response['description'],
            ingredients=response['ingredients'],
            method=response['method']
        )

        return recipe
