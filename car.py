from datetime import datetime


class Carfax:
    def __init__(self, json_data):
        self.make = json_data.get("make", "")
        self.model = json_data.get("model", "")
        self.year = json_data.get("year", "")
        self.min_price = json_data.get("minimumCarfaxValue", "")
        self.max_price = json_data.get("maximumCarfaxValue", "")
        self.record_count = json_data.get("numberOfRecords", "")


class History:  # EpicVin
    def __init__(self, json_data):
        self.made_in = json_data.get("made_in", "")
        self.recalls = json_data.get("recalls", "")

        self.damage = json_data.get("damage_records", "")
        self.auction = json_data.get("auction_records", "")
        self.odometer_problem = json_data.get("odometer_problem", "")
        self.last_price = json_data.get("last_price", "")
        self.last_mileage = json_data.get("last_mileage", "")
        self.img = to_link(json_data.get("img", ""))
        # Sales
        self.sales_count = json_data.get("sales_records", "")
        self.sales = [Sale(sale) for sale in json_data.get("sales", [])]


class Sale:
    def __init__(self, sale):
        self.date = to_date(sale.get("sell_date"))
        self.price = sale.get("price", "")
        self.odometer = sale.get("odometer", "")
        self.sell_type = sale.get("sell_type", "")
        self.images = [to_link(link) for link in sale.get("big_photos", [])]


class Ad:
    def __init__(self, **kwargs):
        for field, value in kwargs.items():
            setattr(self, field, value)


class Car:
    def __init__(self, ad_obj):
        self.ad = Ad(**vars(ad_obj))

    def add_carfax(self, carfax):
        self.carfax = carfax

    def add_history(self, history):
        self.history = history

    def print(self):
        if hasattr(self, "ad"):
            print("Ad Information:")
            print(f"Title: {self.ad.title}")
            print(f"Price: {self.ad.price}")
            print(f"Location: {self.ad.location}")
            print(f"Link: {self.ad.link}")
            print(f"VIN: {self.ad.vin}")
            print(f"Year: {self.ad.year}")
            print(f"Condition: {self.ad.condition}")
            print(f"Title Status: {self.ad.title_status}")
            print(f"Odometer: {self.ad.odometer}")
            print(f"Description: {self.ad.description}")
            print(f"Images: {self.ad.img}")
        else:
            print("No Ad Information")

        if hasattr(self, "carfax"):
            print("\nCarfax Information:")
            print(f"Make: {self.carfax.make}")
            print(f"Model: {self.carfax.model}")
            print(f"Year: {self.carfax.year}")
            print(f"Minimum Price: {self.carfax.min_price}")
            print(f"Maximum Price: {self.carfax.max_price}")
            print(f"Record Count: {self.carfax.record_count}")
        else:
            print("\nNo Carfax Information")

        if hasattr(self, "history"):
            print("\nHistory Information:")
            print(f"Made In: {self.history.made_in}")
            print(f"Recalls: {self.history.recalls}")
            print(f"Damage Records: {self.history.damage}")
            print(f"Auction Records: {self.history.auction}")
            print(f"Odometer Problem: {self.history.odometer_problem}")
            print(f"Last Price: {self.history.last_price}")
            print(f"Last Mileage: {self.history.last_mileage}")
            print(f"Images: {self.history.img}")
            print(f"Sales Count: {self.history.sales_count}")
            if self.history.sales:
                print("Sales:")
                for sale in self.history.sales:
                    print(
                        f"Date: {sale.date}, Price: {sale.price}, Odometer: {sale.odometer}, Sell Type: {sale.sell_type}, Images: {sale.images}"
                    )
        else:
            print("\nNo History Information")


def to_date(seconds):
    return datetime.fromtimestamp(seconds).strftime("%m / %Y")


def to_link(bad_link):
    return bad_link.replace("\\", "")
