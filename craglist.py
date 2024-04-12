import requests
from bs4 import BeautifulSoup
from car import Car
from epicvin import epicvin_info
from carfax import carfax_price_range

url = "https://inlandempire.craigslist.org/search/mira-loma-ca/cta"
models = [
    {"auto_make_model": "toyota"},  # rav4, highlander
    {"auto_make_model": "honda"},  # crv
    {"auto_make_model": "subaru"},  # forester
    {"auto_make_model": "mazda"},  # cx-5
    {"auto_make_model": "nissan"},  # rogue
]
parameters = {
    "auto_bodytype": "10",  # suv
    "min_price": "5000",
    "max_price": "20000",
    "min_auto_year": "2014",
    "max_auto_year": "2018",
    "max_auto_miles": "75000",
    "search_distance": "150",
    "lat": "33.9729",
    "lon": "-117.4961",
    "bundleDuplicates": "1",
    "hasPic": "1",
}


def read_feed():
    cars = []
    for model in models:
        params = {**model, **parameters}
        car_list = craigslist_search(params)
        cars.extend(car_list)
    print("Total cars: ", len(cars))
    cars = list(filter(is_good_car, cars))
    print("Remining cars: ", len(cars))
    print([car.ad.link for car in cars])

    return cars


def craigslist_search(params):
    soup = send_get_request(url, params)
    search_results = soup.find_all("li", class_="cl-static-search-result")
    return [process_car(item) for item in search_results]


def is_good_car(car):
    return (
        car.ad.vin
        and car.ad.price
        and car.ad.price < car.carfax.max_price
        and car.ad.title_status
        and car.ad.title_status.lower() == "clean"
        and car.history.damage < 1
        and car.history.odometer_problem < 1
        and car.history.sales_count < 5
    )


def process_car(item):
    cragslist_ad = CragslistAd(item)
    car = Car(cragslist_ad)
    if cragslist_ad.vin:
        car.add_carfax(carfax_price_range(cragslist_ad.vin))
        car.add_history(epicvin_info(cragslist_ad.vin))
    return car


class CragslistAd:
    def __init__(self, item):
        self.title = find_text(item, "div.title")
        self.price = find_text(item, "div.price")
        self.location = find_text(item, "div.location")
        self.link = find_link(item)
        # get car details
        soup = send_get_request(self.link)
        self.vin = find_text(soup, "div.attr.auto_vin span.valu")
        self.year = find_text(soup, "span.valu.year")
        self.condition = find_text(soup, "div.attr.condition span.valu")
        self.title_status = find_text(soup, "div.attr.auto_title_status span.valu")
        self.odometer = find_text(soup, "div.attr.auto_miles span.valu")
        self.description = find_text(soup, "section#postingbody")
        self.img = get_pics(soup)


def find_text(soup, selector):
    element = soup.select_one(selector)
    return element.text.strip() if element else None


def find_link(soup):
    element = soup.find("a")
    return element["href"] if element else None


def get_pics(soup):
    thumbs = soup.find(id="thumbs")
    a_list = thumbs.find_all("a", class_="thumb") if thumbs else []
    return [a["href"] for a in a_list]


def send_get_request(url, params=None):
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx and 5xx status codes)
        return BeautifulSoup(response.content, "html.parser")
    except requests.exceptions.RequestException as e:
        print(f"Error sending GET request to Cragslist: {e}")
        return None


read_feed()
