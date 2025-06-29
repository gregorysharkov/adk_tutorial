# mock get weather service

WEATHER_DICT = {
    "Hong Kong": {
        "temperature": 35,
        "weather": "showers",
    },
    "London": {
        "temperature": 17,
        "weather": "cloudy",
    },
    "Paris": {
        "temperature": 20,
        "weather": "sunny",
    },
}


def get_weather(city: str) -> dict:
    """
    Mock weather API call

    Args:
        city (str): The name of the city (e.g., "New York", "London", "Tokyo").

    Returns:
        dict: A dictionary containing the weather information.
              Includes a 'status' key ('success' or 'error').
              If 'success', includes a 'report' key with weather details.
              If 'error', includes an 'error_message' key.
    """
    city_weather = WEATHER_DICT.get(city)

    if not city_weather:
        return {"status": "error", "message": f"City {city} not found"}

    return {"status": "success", "weather": city_weather}
