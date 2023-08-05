import requests


class Weather:
    """Create a Weather object to get weather data from OpenWeatherMap API.
    
    Package use example:
    
    # Create a weather object using a city name.
    # Get your own API_KEY from https://openweathermap.org
    >>> weather = Weather(apikey="[API_KEY]", city="rome")
    
    # Get complete data for the next 12 hours.
    >>> weather.next_12h()
    
    # Simplified data for the next 12 hours.
    >>> weather.next_12h_simplified()
    """
    def __init__(self, apikey: str, city: str) -> None:
        url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={apikey}&units=metric"
        r = requests.get(url)
        self.data = r.json()
        if self.data["cod"] != "200":
            raise ValueError(self.data["message"])
    
    def next_12h(self):
        return self.data['list'][:4]
    
    def next_12h_simplified(self):
        simple_data = []
        for dicty in self.next_12h():
            simple_data.append((
                dicty['dt_txt'],
                dicty['main']['temp'],
                dicty['weather'][0]['description']
            ))
        return simple_data
