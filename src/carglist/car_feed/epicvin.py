import requests
from car import History

api_key = "7d9d2a81-c8bd-4e72-ad32-1de6fa499017"
url = "https://api.epicvin.com/check"


def epicvin_info(vin):
    print(f"[{vin}] Pull EpicVin info")
    params = {"key": api_key, "vin": vin}
    json_response = send_get_request(url, params)
    # print(json_response)
    return History(json_response.get("data")) if json_response else None


def send_get_request(url, params=None):
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx and 5xx status codes)
        return response.json()  # Assuming the response is JSON data
    except requests.exceptions.RequestException as e:
        print(f"Error sending GET request: {e}")
        return None


# Example usage:
# vin_number = "JTJGK31U670006257"
# epicvin_data = epicvin_info(vin_number)
# print(vars(epicvin_data))
