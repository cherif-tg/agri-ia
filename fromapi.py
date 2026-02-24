from weather_api import WeatherAPI

api = WeatherAPI(api_key="92e660dc278734243389e9aef46a3dde", provider="openweathermap")
meteo = api.get_weather("Maritime")