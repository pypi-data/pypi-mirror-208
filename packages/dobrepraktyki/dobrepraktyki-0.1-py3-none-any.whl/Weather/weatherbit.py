import requests


class WeatherBit:
    def __init__(self, city):
        self.city = city
        self.api_key = "df889d79c28b4bfcafd514b9919bccba"

    def forecast_weather(self, days):
        tmp = {}
        url = f"https://api.weatherbit.io/v2.0/forecast/daily?city={self.city}&days={days}&key={self.api_key}"

        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

            for forecast in data["data"]:
                date = forecast["valid_date"]
                max_temp = forecast["max_temp"]
                min_temp = forecast["min_temp"]
                condition = forecast["weather"]["description"]

                tmp.update({date: {"max_temp": max_temp,
                                   "min_tem": min_temp,
                                   "condition": condition}})
            return tmp
        return None
