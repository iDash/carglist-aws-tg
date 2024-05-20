from datetime import datetime


class Carfax:
    def __init__(self, json_data):
        self.make = json_data.get("make", "")
        self.model = json_data.get("model", "")
        self.year = int(json_data.get("year", "0"))
        self.min_price = int(json_data.get("minimumCarfaxValue", "0").replace(",", ""))
        self.max_price = int(json_data.get("maximumCarfaxValue", "0").replace(",", ""))
        self.record_count = int(json_data.get("numberOfRecords", "0"))


class History:  # EpicVin
    def __init__(self, json_data):
        self.made_in = json_data.get("made_in", "")
        self.recalls = int(json_data.get("recalls", "0"))
        self.damage = int(json_data.get("damage_records", "0"))
        self.auction = int(json_data.get("auction_records", "0"))
        self.odometer_problem = int(json_data.get("odometer_problem", "0"))
        self.last_price = int(json_data.get("last_price", "0"))
        self.last_mileage = int(json_data.get("last_mileage", "0"))
        self.images = to_link(json_data.get("img", ""))
        # Sales
        self.sales_count = int(json_data.get("sales_records", "0"))
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
    def __init__(self):
        ad = {}

    def add_ad(self, ad_class_obj):
        posted_date = datetime.fromisoformat(ad_class_obj.posted_str.split("T")[0])
        ad_obj = {"posted": posted_date, **vars(ad_class_obj)}
        self.ad = Ad(**ad_obj)

    def add_carfax(self, carfax):
        self.carfax = carfax
        if hasattr(self, "ad"):
            self.discount = round((1 - self.ad.price / carfax.max_price) * 100)

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
            if self.ad.images:
                print("Ad Images:")
                for img in self.ad.images:
                    print(img)
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
            print(f"History Images: {self.history.images}")
            print(f"Sales Count: {self.history.sales_count}")
            if self.history.sales:
                print("Sales:")
                for sale in self.history.sales:
                    print(
                        f"Date: {sale.date}, Price: {sale.price}, Odometer: {sale.odometer}, Sell Type: {sale.sell_type}"
                    )
                    if sale.images:
                        print("Sale Images:")
                        for img in sale.images:
                            print(img)
        else:
            print("\nNo History Information")

    def html(self):
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{self.ad.title}</title>
            <style>
                .container {{
                    display: grid;
                    grid-template-columns: repeat(3, 1fr);
                    gap: 20px;
                }}
                .description {{
                    grid-column: span 3;
                }}
                .images, .sales {{
                    display: grid;
                    grid-template-columns: repeat(3, 1fr);
                    gap: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="ad-info">
                    <h2>Ad Info</h2>
                    <ul>
                        
                        <li><strong>Title:</strong> {self.ad.title}</li>
                        <li><strong>Price:</strong> {self.ad.price} (Last: {self.history.last_price})</li>
                        <li><strong>Range:</strong> {self.carfax.min_price} - {self.carfax.max_price} (Discount: <strong>{self.discount}%</strong>)</li>
                        <li><strong>Odometer:</strong> {self.ad.odometer} (Last milage:  {self.history.last_mileage})</li>
                        <li><strong>Records Count:</strong> {self.carfax.record_count}</li>
                        <li><strong>Sales Count:</strong> {self.history.sales_count}</li>
                        <li><strong>Recalls:</strong> {self.history.recalls}</li>
                    </ul>
                </div>
                <div class="carfax-info">
                    <h2>Car Info</h2>
                    <ul>
                        <li><strong>VIN:</strong> {self.ad.vin}</li>
                        <li><strong>Make:</strong> {self.carfax.make}</li>
                        <li><strong>Model:</strong> {self.carfax.model}</li>
                        <li><strong>Year:</strong> {self.ad.year} (Real: {self.carfax.year})</li>
                        <li><strong>Made In:</strong> {self.history.made_in}</li>
                        <li><strong>Title Status:</strong> {self.ad.title_status} (condition: {self.ad.condition})</li>
                        <br/>
                        <li><strong>Location:</strong> {self.ad.location}</li>
                        <li><strong>Link:</strong> <a href="{self.ad.link}">Link to Cragslist</a></li>
                        <li><strong>Posted:</strong> {self.ad.posted}</li>
                    </ul>
                </div>
                <div class="history-info">
                    <h2>History Info</h2>
                    <ul>
                        <li><strong>Damage Records:</strong> {self.history.damage}</li>
                        <li><strong>Auction Records:</strong> {self.history.auction}</li>
                        <li><strong>Odometer Problem:</strong> {self.history.odometer_problem}</li>

                    </ul>
                </div>
            </div>
            <div class="description">
                <h2>Description</h2>
                <p>{self.ad.description}</p>
            </div>
            <h2>Ad Images</h2>
            <div class="images">
        """

        for image in self.ad.images:
            html_content += f"<img src='{image}' alt='Car Image'>"

        html_content += f"""
            </div>
            <h2>Sales</h2>
            <div class="sales">
        """

        for sale in self.history.sales:
            html_content += f"""
                <ul>
                    <li>Date: {sale.date}, Price: {sale.price}, Odometer: {sale.odometer}, Sell Type: {sale.sell_type}</li>
            """

            for img in sale.images:
                html_content += f"<li><img src='{img}' alt='Sale Image'></li>"

            html_content += """
                </ul>
            """

        html_content += """
            </div>
        </body>
        </html>
        """

        return html_content


def to_date(seconds):
    return datetime.fromtimestamp(seconds).strftime("%m / %Y")


def to_link(bad_link):
    return bad_link.replace("\\", "")
