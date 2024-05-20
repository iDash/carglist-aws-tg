import requests
from bs4 import BeautifulSoup
from car import Car
from epicvin import epicvin_info
from carfax import carfax_price_range

url = "https://losangeles.craigslist.org/search/boron-ca/cta"
# current 22 mpg (20-26)
models = [
    {"auto": "toyota rav4", "years": range(2013, 2018)},  # target 25mpg (23-29)
    {"auto": "honda crv", "years": [2009, 2010, 2011, 2012, 2013, 2016]},
    {"auto": "honda cr-v", "years": [2009, 2010, 2011, 2012, 2013, 2016]},
    {"auto": "honda pilot", "years": [2007, 2008, 2010, 2012, 2014, 2015, 2017, 2018]},
    {"auto": "hyundai tucson", "years": [2007, 2009, 2019, 2020, 2021, 2022]},
    {"auto": "mazda cx5", "years": [2013, 2015, 2017, 2020]},
    {"auto": "mazda cx-5", "years": [2013, 2015, 2017, 2020]},
    {"auto": "nissan rogue", "years": [2017, 2018, 2019, 2020, 2022]},
    {"auto": "ford escape", "years": range(2015, 2019)},
    {"auto": "subaru forester", "years": [2016, 2018, 2021, 2022]},
    {"auto": "chevrolet equinox", "years": [2016, 2017, 2019, 2020, 2021]},
    # {"auto": "lexus rx", "years": [2008, 2009, 2011, 2012, 2013, 2014, 2015]},
]

parameters = {
    # "purveyor": "owner",  # sold by owner
    "auto_bodytype": "10",  # suv
    "min_price": "5000",
    "max_price": "20000",
    # "min_auto_year": "2010",
    # "max_auto_year": "2019",
    # "min_auto_miles": "80000",
    # "max_auto_miles": "90000",
    "search_distance": "200",
    "lat": "33.9729",
    "lon": "-117.4961",
    "bundleDuplicates": "1",
    # "hasPic": "1",
    "sort": "priceasc",
}
whitelist = ["father", "mother", "died", "passed away"]
blacklist = ["salvage"]


# Entry point
def search():
    params_list = compile_params()
    print("Searches in the feed: ", len(params_list))
    feed = generate_feed(params_list)
    print("Cars to process: ", len(feed))
    cars = process_feed(feed)
    print(f"Selected {len(cars)} / {len(feed)} cars")
    return cars


def compile_params():
    miles_per_year = 10000
    params_list = []
    for model in models:
        for year in model["years"]:
            params = {
                "auto_make_model": model["auto"],
                "min_auto_year": year,
                "max_auto_year": year,
                "max_auto_miles": min(80000, miles_per_year * (2024 - year)),
                **parameters,
            }
            params_list.append(params)
    return params_list


def generate_feed(params_list):
    feed = []
    print("Generating feed:")
    for params in params_list:
        try:
            soup = send_get_request(url, params)
        except Exception as e:
            print(f"Couldnt run cragslist search {e}")

        search_results = soup.find_all("li", class_="cl-static-search-result")
        print(
            f"{params['auto_make_model']}-{params['min_auto_year']}: {len(search_results)}"
        )
        feed.extend(search_results)
    return feed


def process_feed(feed):
    cars = []
    for item in feed:
        car = craigslist_details(item)
        if car:
            cars.append(car)
    return cars


def craigslist_details(item):
    try:
        car = process_car(item)
        if is_good_car(car):
            save_to_file(car)
            return car
    except Exception as e:
        print(f"ERROR retriving car details {e}")


def is_good_car(car):
    return (
        car.ad.vin
        and car.ad.price < car.carfax.max_price + 500
        and car.history.damage < 1
        and car.history.auction < 1
        and car.history.odometer_problem < 1
        # and max(int(car.ad.odometer), int(car.history.last_mileage)) #embeded in params
        # < 10000 * (2024 - int(car.ad.year))
        # and car.history.sales_count < 5
        and (
            car.ad.title_status != None
            and car.ad.title_status.lower() == "clean"
            or car.ad.blacklist_count == 0
        )
        or car.ad.whitelist_count > 0
    )


def save_to_file(car):
    info = (
        f"{car.ad.price}_{car.discount}_{car.ad.odometer}"
        if hasattr(car, "ad")
        else "no_info"
    )
    filename = f"{car.carfax.make}-{car.carfax.model}_{car.carfax.year}_{info}.html"
    folder = "owners" if hasattr(parameters, ("purveyor")) else "all"
    with open(f"./listings/{folder}/" + filename, "w") as file:
        file.write(car.html())


def process_car(item):
    cragslist_ad = CragslistAd(item)
    car = Car()
    car.add_ad(cragslist_ad)
    if cragslist_ad.vin:
        car.add_carfax(carfax_price_range(cragslist_ad.vin))
        car.add_history(epicvin_info(cragslist_ad.vin))
    return car


class CragslistAd:
    def __init__(self, item):
        try:
            self.title = find_text(item, "div.title")
            price = find_text(item, "div.price")
            self.price = int(price.replace("$", "").replace(",", ""))
            self.location = find_text(item, "div.location")
            self.link = find_link(item)
            # get car details
            soup = send_get_request(self.link)
            self.vin = find_text(soup, "div.attr.auto_vin span.valu")
            self.year = find_int(soup, "span.valu.year")
            self.condition = find_text(soup, "div.attr.condition span.valu")
            self.title_status = find_text(soup, "div.attr.auto_title_status span.valu")
            self.odometer = find_int(soup, "div.attr.auto_miles span.valu")
            self.description = find_text(soup, "section#postingbody")
            self.posted_str = soup.find("p", id="display-date").find("time")["datetime"]
            self.images = get_pics(soup)
            self.whitelist_count = len(
                list(filter(lambda x: x in self.description, whitelist))
            )
            self.blacklist_count = len(
                list(filter(lambda x: x in self.description, blacklist))
            )
        except Exception as e:
            print(f"Error processing Cragslist Ad: \n{self.link}")


def find_text(soup, selector):
    element = soup.select_one(selector)
    return element.text.strip() if element else None


def find_int(soup, selector):
    element = soup.select_one(selector)
    return element.text.strip() if element else 0


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


search()


# def process_car_vin(vin):
#     car = Car()
#     car.add_carfax(carfax_price_range(vin))
#     car.add_history(epicvin_info(vin))
#     print(car.print())
#     save_to_file(car)


# process_car_vin("5YJXCBE22HF041805")
