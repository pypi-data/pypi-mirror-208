import requests


class Shazam:
    def __init__(self):
        self.api_key = "713d8703ecmsh49ae514a91c411ap1fa48fjsn27daa917c41e"

    def complete(self, text):
        url = "https://shazam.p.rapidapi.com/auto-complete"

        headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": "shazam.p.rapidapi.com",
        }

        response = requests.get(url, headers=headers, params={"term": text})

        if response.status_code == 200:
            suggestions = response.json()["hints"]
            return suggestions
        else:
            print(f"Błąd {response.status_code}: {response.text}")
