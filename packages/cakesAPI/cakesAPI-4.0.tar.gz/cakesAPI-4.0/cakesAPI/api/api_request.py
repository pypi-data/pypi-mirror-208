import requests


class RequestAPI:
    def __init__(self, api_key):
        self.api_key = api_key

    def send_request(self, url):
        headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "the-birthday-cake-db.p.rapidapi.com"
        }
        response = requests.get(url, headers=headers)
        return response.json()
