import requests


class Weather:
    def __init__(self, city):
        self.api_key = "433e34d6986e4aceb2f171953231505"
        self.city = city

    def check_weather(self):
        url = f"https://api.weatherapi.com/v1/current.json?key={self.api_key}&q={self.city}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            return data['current']['temp_c'], data['current']['condition']['text']
            # print(f"Aktualna temperatura w {self.city}: {data['current']['temp_c']}°C")
            # print(f"Warunki pogodowe: {data['current']['condition']['text']}")
        return None

    def forecast_weather(self, days):
        tmp = {}
        url = f"https://api.weatherapi.com/v1/forecast.json?key={self.api_key}&q={self.city}&days={days}"

        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

            for forecast in data["forecast"]["forecastday"]:
                date = forecast["date"]
                max_temp = forecast["day"]["maxtemp_c"]
                min_temp = forecast["day"]["mintemp_c"]
                condition = forecast["day"]["condition"]["text"]

                tmp.update({date: {"max_temp": max_temp,
                                   "min_tem": min_temp,
                                   "condition": condition}})
            return tmp
        return None
