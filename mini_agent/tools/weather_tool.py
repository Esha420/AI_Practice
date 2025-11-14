#tools/weather_tool.py
import requests

import os
API_KEY = os.getenv("OPENWEATHER_API_KEY")

def weather_tool(city):
    """
    Fetch current weather for a city dynamically using OpenWeatherMap API.
    """
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={API_KEY}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return f"Weather data not found for {city}."
        data = response.json()
        temp = data["main"]["temp"]
        description = data["weather"][0]["description"]
        return f"{temp}°C, {description}"
    except Exception as e:
        return f"Error fetching weather: {e}"
