import requests
import json
from car import Carfax

carfax_url = "https://pos.secure.carfax.com/vehicleDataByVin"
headers = {"content-type": "application/json"}


def carfax_price_range(vin):
    print(f"[{vin}] Pull Carfax info")
    data = {"vin": vin}
    json_response = send_post_request(carfax_url, headers, json.dumps(data))
    return Carfax(json_response) if json_response else None


def send_post_request(url, headers, data):
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx and 5xx status codes)
        return response.json()  # Assuming the response is JSON data
    except requests.exceptions.RequestException as e:
        print(f"Error sending POST request: {e}")
        return None


# Example usage:
# vin_number = "5XYKT3A1XCG259070"
# carfax_data = carfax_price_range(vin_number)
# print(vars(carfax_data))
