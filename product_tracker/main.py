import json
from collections import namedtuple
import bs4
import webbrowser
import re
import requests
import os
from logo import logo
from tqdm import tqdm
from time import sleep
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

EMAIL = os.environ.get("SENDER_EMAIL")
PASS = os.environ.get("SENDER_PASS")

HEADERS = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,"
                     "application/signed-exchange;v=b3;q=0.9",
           "Pragma": "no-cache",
           "Upgrade-Insecure-Requests": "1",
           "Host": "www.amazon.sa",
           "Accept-Language": "en,ar;q=0.9,en-GB;q=0.8,en-US;q=0.7",
           "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/97.0.4692.99 Safari/537.36 Edg/97.0.1072.76",
           }

AMAZON_DOMAINS = ['.eg', '.br', '.ca', '.mx', '.com', '.cn', '.in', '.jp', '.sg', '.ae', '.sa', '.fr', '.de', '.it',
                  '.nl', '.pl', '.es', '.se', '.tr', '.uk', '.au']


def get_product_link():
    product_link = input("Please, Paste you Amazon product url link here : \n")
    product_name = input("Write what is the product name? \n").title()
    pattern = re.compile(r"(https://www\.amazon)(\.co\.uk|\.com|\.sa)")
    matches = pattern.finditer(product_link)
    for match in matches:
        # Amazon link without the domain
        amazon_link = match.group(1)
        amazon_domain = match.group(2)
        # Amazon Domain Store
        if amazon_link == "https://www.amazon":
            print("Please wait while processing your request")
            print(f"Your amazon related to {amazon_domain} domain.")
            if amazon_domain in AMAZON_DOMAINS:
                if amazon_domain == ".sa":
                    Product = namedtuple("Product", ["url", "name", "domain"])
                    target_product = Product(url=product_link, name=product_name, domain=amazon_domain)
                    return sa_request_amazon_product_data(target_product)
                else:
                    print("For now our app just supporting Amazon SA domain.")
                    return False
            else:
                print(f"This {match.group(2)} Amazon domain are not supported yet.")
                return False
        else:
            print("Please, get a product from amazon website only")
            return False


def sa_request_amazon_product_data(product_info: namedtuple) -> namedtuple:
    url_link = product_info.url
    product_name = product_info.name
    domain = product_info.domain
    r = requests.get(url=url_link, headers=HEADERS)
    data = r.text
    soup = bs4.BeautifulSoup(data, 'lxml')
    current_price = soup.find_all(name='span', class_="a-price-whole")
    price_symbol = soup.find_all(name='span', class_="a-price-symbol", dir="rtl")
    current_price = current_price[0].getText()
    filter_price = re.compile(r"(\d*)")
    match = filter_price.match(current_price)
    product_price = match.group()
    price_symbol = price_symbol[0].getText()
    print(f"The price of this product is : {current_price}{price_symbol}")
    target_price = input("What is the target price for this product ? : ")
    Product_info = namedtuple("Product", ["name", "link", "domain", "price", "currency", "target_price"])
    product_info = Product_info(name=product_name, link=url_link, domain=domain, price=product_price,
                                currency=price_symbol,
                                target_price=target_price)
    return product_info


def com_request_amazon_product_data(url_link, product):
    r = requests.get(url=url_link, headers=HEADERS)
    with open(f"{product}.html", 'w', encoding='utf-8') as p_file:
        p_file.write(r.text)
    with open(f'{product}.html', encoding='utf-8') as html_f:
        p_data = html_f.read()
    soup = bs4.BeautifulSoup(p_data, 'lxml')
    price = soup.find_all(name='span', class_="a-price-whole")
    price_symbol = soup.find_all(name='span', class_="a-price-symbol", dir="rtl")
    print(f"The price of this product is :{price[0].getText()}{price_symbol[0].getText()}")


def dumb_data(data):
    with open("product_tracker.json", "w", encoding="utf-8") as tacker_file:
        json.dump(data, tacker_file, indent=4)


def update_date(data):
    with open("product_tracker.json", "r", encoding="utf-8") as tacker_file:
        file_data = json.load(tacker_file)
        file_data.update(data)
    with open("product_tracker.json", "w", encoding="utf-8") as tacker_file:
        json.dump(file_data, tacker_file, indent=4)


def save_product_data(data: namedtuple):
    print("We are working on creating a tracking file information ..Please wait!!!")
    product_name = str(data.name)
    product_link = str(data.link)
    product_domain = str(data.domain)
    product_price = str(data.price)
    product_currency = str(data.currency)
    product_user_price = str(data.target_price)
    new_data = {
        product_name: {
            "product_link": product_link,
            "product_price": product_price,
            "product_domain": product_domain,
            "product_currency": product_currency,
            "product_user_price": product_user_price
        }
    }
    try:
        if os.path.isfile("product_tracker.json"):
            update_date(new_data)
        else:
            dumb_data(new_data)
    except Exception as r:
        print(f"There is an error sorry for that :(\n{r}")

    else:
        process = [_ for _ in tqdm(range(10)) if sleep(0.3) is None]
        print(f"You tracking file info about {product_name} is ready.")


def track_prices():
    with open("product_tracker.json", "r", encoding="utf-8") as products_file:
        data = json.load(products_file)
        all_products = list(data.keys())
        print("Please check which product you looking to check?")
        products_keys = {}
        for index, product in enumerate(all_products, start=1):
            print(f"{index}- {product}")
            products_keys[index] = product
        choose_product = int(input("Which product you looking to check if the price was dropped ?"))
        if choose_product in products_keys:
            product_info = data[products_keys[choose_product]]
            product_price = product_info['product_price']
            product_domain = product_info["product_domain"]
            product_currency = product_info["product_currency"]
            product_user_price = product_info["product_user_price"]
            product_link = product_info["product_link"]
            print(f"You chose \n{products_keys[choose_product]}\n{'_' * 18}\n|Product Details|\n{'-' * 18}")
            print(f"The current price for this product is {product_price}\n"
                  f"The product was found under Amazon{product_domain}\n"
                  f"And The currency of it is {product_currency}\n"
                  f"You put a price of {product_user_price}{product_currency} for this product.")
            do_visit = input("Do you want to visit this product web page?").lower()
            if do_visit:
                webbrowser.open(product_link)


def send_email():
    with open("product_tracker.json", "r", encoding="utf-8") as products_file:
        data = json.load(products_file)
        for key, value in data.items():
            current_price = int(value["product_price"])
            user_price = int(value["product_user_price"])
            product_currency = value["product_currency"]
            product_link = value["product_link"]
            if current_price < user_price:
                msg = MIMEMultipart('alternative')
                msg["Subject"] = f"🤩Amazon {key} product price drop🤩"
                msg["From"] = EMAIL
                msg["To"] = EMAIL
                text = f"WE have good news for you!!!" \
                       f"\nThe price of {key} product was dropped." \
                       f"\nYou have the chance to get this product for {current_price}{product_currency}\n" \
                       f"This is the product link to check\n" \
                       f"{product_link}"
                html =f"""\
                <html>
                    <head></head>
                    <body>
                        <h2>WE have good news for you!<br>
                        The price of {key} product was dropped.<br>
                        You have the chance to get this product for {current_price}{product_currency}<br>
                        This is the product link to check<br>
                        <a href={product_link}>Your Product waiting for you</a>
                        </h2>
                    </body>
                </html>
                """
                part1= MIMEText(text, 'plain')
                part2= MIMEText(html, 'html')
                msg.attach(part1)
                msg.attach(part2)
                with smtplib.SMTP_SSL("smtp.gmail.com", port=465) as connection:
                    connection.login(EMAIL, PASS)
                    connection.send_message(msg)
                    print("😇😇WoooW we found a good deal for you wait ...please  🤑  🤑 ")
                    proccess = [_ for _ in tqdm(range(10)) if sleep(0.3) is None]
                    print(f"🥳We send an Email we will be happy see you🥳")
            else:
                print(f"😰The {key} product didn't drop wait be patient😅 ")

def main():
    print(logo)
    print("Welcome to Amazon products Tracker.")
    product_data = get_product_link()
    try:
        print("Please wait >>>> 🥰\n")
        save_data = input("Do you want to track this product : \n").lower()
    except Exception as r:
        print(f"We can't processed you request\n{r}")
    else:
        if save_data == "y":
            save_product_data(product_data)

    do_check = input("Do you want to check all product you add?").lower()
    if do_check == "y":
        track_prices()
    do_check_track_file = input("Do you want to check the track file?\n").lower()
    if do_check_track_file == "y":
        send_email()


if __name__ == "__main__":
    main()
