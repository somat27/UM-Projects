import json
import socket
import time
import requests

COLOR_SUCCESS = '\033[92m'
COLOR_ERROR = '\033[91m'
COLOR_RESET = '\033[0m'

PRODUCERS_FILE = 'Data/Producers.json'

purchased_subscriptions = {}
resale_fees = {}
DEFAULT_RESALE_FEE = 10.0

MANAGER_IP = '193.136.11.170'
MANAGER_PORT = 5001

# -----------------------------
# Manager / REST discovery
# -----------------------------

def get_producers_rest():
    url = f"http://{MANAGER_IP}:{MANAGER_PORT}/producer"
    try:
        response = requests.get(url, timeout=2)
        return response.json() or []
    except requests.exceptions.RequestException as e:
        print(f"Error getting REST producers: {e}")
        return []


def get_producer_categories_rest(ip, port):
    url = f"http://{ip}:{port}/categories"
    try:
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error getting categories via REST: {response.status_code} - {response.text}")
            return []
    except requests.exceptions.RequestException:
        return []


def buy_product_rest(producer_info, product_name, quantity):
    url = f"http://{producer_info['IP']}:{producer_info['PORT']}/buy/{product_name}/{quantity}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"{COLOR_SUCCESS}Success: {COLOR_RESET}Purchase completed for {product_name} (Quantity: {quantity}).")
        else:
            print(f"{COLOR_ERROR}Error: {COLOR_RESET}Failed to buy {product_name}: Status code {response.status_code}.")
    except requests.exceptions.RequestException as e:
        print(f"{COLOR_ERROR}Error: {COLOR_RESET}Failed to buy {product_name}: {e}")


def get_categories_rest():
    available_producer_cats = []
    rest_producers = get_producers_rest()

    for rest_producer in rest_producers:
        ip = rest_producer.get('ip') or rest_producer.get('IP')
        port = rest_producer.get('port') or rest_producer.get('PORT') or rest_producer.get('porta')
        name = rest_producer.get('name') or rest_producer.get('Name') or rest_producer.get('nome')

        if not ip or not port:
            continue

        existing = None
        for producer in available_producer_cats:
            if producer["IP"] == ip and producer["PORT"] == port:
                existing = producer
                break

        categories = get_producer_categories_rest(ip, port)
        if not categories:
            continue

        if not existing:
            available_producer_cats.append({
                "Name": name or f"{ip}:{port}",
                "IP": ip,
                "PORT": port,
                "Connection": "REST",
                "Categories": set(categories)
            })
        else:
            existing["Categories"].update(categories)

    # convert sets to lists
    for producer in available_producer_cats:
        producer["Categories"] = list(producer["Categories"])

    return available_producer_cats


# -----------------------------
# Socket discovery
# -----------------------------

def get_producers_socket():
    active_socket_producers = []
    try:
        with open(PRODUCERS_FILE, 'r', encoding='utf-8') as f:
            file_producers = json.load(f)
    except Exception as e:
        print(f"Error reading {PRODUCERS_FILE}: {e}")
        return active_socket_producers

    for socket_producer in file_producers:
        ip = socket_producer.get('IP')
        port = socket_producer.get('Port') or socket_producer.get('PORT')
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2)
                result = s.connect_ex((ip, int(port)))
                if result == 0:
                    active_socket_producers.append({
                        "Name": socket_producer.get('Name') or f"{ip}:{port}",
                        "IP": ip,
                        "PORT": int(port),
                        "Connection": "Socket"
                    })
        except Exception as e:
            print(f"Error testing connection with {ip}:{port}: {e}")
    return active_socket_producers


def get_categories_socket():
    available_socket_cats = []
    active_socket_producers = get_producers_socket()

    for socket_producer in active_socket_producers:
        ip = socket_producer['IP']
        port = socket_producer['PORT']
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2)
                s.connect((ip, port))
                s.sendall("LIST_CATEGORIES".encode('utf-8'))  # expects server-side support
                data = s.recv(1024).decode()
                categories = data.split("\n")[1:] if data else []
                categories = [c for c in categories if c]
                if categories:
                    available_socket_cats.append({
                        "Name": socket_producer['Name'],
                        "IP": ip,
                        "PORT": port,
                        "Connection": "Socket",
                        "Categories": categories
                    })
                else:
                    print(f"No categories found for {socket_producer['Name']}")
        except Exception as e:
            print(f"Error connecting to {ip}:{port} to get categories: {e}")
    return available_socket_cats


# -----------------------------
# Product retrieval per category
# -----------------------------

def get_products_by_category(producer, chosen_category):
    products = []
    if producer['Connection'] == "Socket":
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(10)
                try:
                    s.connect((producer['IP'], producer['PORT']))
                    request_msg = f"LIST_PRODUCTS_CATEGORY,{chosen_category}"
                    s.sendall(request_msg.encode('utf-8'))
                    response = s.recv(4096).decode('utf-8')
                    products = json.loads(response)
                except socket.timeout:
                    print(f"Error: Timeout while connecting to producer {producer['IP']}:{producer['PORT']}")
                except Exception as e:
                    print(f"Unexpected error connecting to producer: {e}")
        except Exception as e:
            print(f"Error connecting to producer {producer['IP']}:{producer['PORT']}. Details: {e}")
        return products

    elif producer['Connection'] == "REST":
        url = f"http://{producer['IP']}:{producer['PORT']}/products?category={chosen_category}"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Request error to {producer['IP']}:{producer['PORT']}. Status code: {response.status_code}")
                return []
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to producer {producer['IP']}:{producer['PORT']}. Details: {e}")
            return []


# -----------------------------
# Listing & buying
# -----------------------------

def list_products(products_for_category):
    print("\nProducts available to purchase:")
    product_id = 1
    for producer_info in products_for_category:
        print(f"Producer: {producer_info['Name']} ({producer_info['IP']}:{producer_info['PORT']}) - Connection: {producer_info['Connection']}")
        for product in producer_info['Products']:
            # Support both English and legacy Portuguese keys
            name = product.get('product') or product.get('produto') or product.get('Name')
            price = product.get('price') or product.get('preco') or product.get('Price')
            quantity = product.get('quantity') or product.get('quantidade') or product.get('Quantity')
            product['__display_name'] = name
            product['__display_price'] = price
            product['__display_quantity'] = quantity
            print(f"{product_id}. Product: {name} - Price: {price} - Available: {quantity}")
            product['__id'] = product_id
            product_id += 1


def buy_product_socket(producer_info, product_name, quantity):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(30)
            sock.connect((producer_info['IP'], producer_info['PORT']))
            msg = f"SUBSCRIBE_PRODUCT,{product_name},{quantity}"
            sock.sendall(msg.encode('utf-8'))
            reply = sock.recv(1024).decode('utf-8')
            if reply == "OK":
                print(f"{COLOR_SUCCESS}Success: {COLOR_RESET}Purchase completed for {product_name} (Quantity: {quantity}).")
            else:
                print(f"{COLOR_ERROR}Error: {COLOR_RESET}Failed to buy {product_name}: {reply}")
    except socket.timeout:
        print(f"{COLOR_ERROR}Error: {COLOR_RESET}Timeout while connecting to producer {producer_info['IP']}:{producer_info['PORT']}.")
    except Exception as e:
        print(f"{COLOR_ERROR}Error: {COLOR_RESET}Error trying to buy product {product_name}: {e}")


def buy_products(products_for_category, chosen_ids):
    # Flatten products for quick selection
    flat = []
    for producer_info in products_for_category:
        for product in producer_info['Products']:
            flat.append((producer_info, product))

    # Process selections
    for pid in chosen_ids:
        match = next(((pinfo, p) for (pinfo, p) in flat if p.get('__id') == pid), None)
        if not match:
            print(f"Product with ID {pid} not found.")
            continue

        producer_info, product = match
        name = product.get('__display_name')
        price = float(product.get('price') or product.get('preco') or product.get('Price') or 0)
        available = int(product.get('__display_quantity') or 0)

        if available == 0:
            print(f"Sorry, {name} is out of stock.")
            continue

        try:
            desired = int(input(f"How many units of {name} do you want? Available: {available} "))
        except ValueError:
            print("Invalid quantity. Please enter a number.")
            continue

        if desired <= 0:
            print("Quantity must be greater than zero.")
            continue
        if desired > available:
            print(f"Sorry, only {available} units of {name} are available.")
            continue

        # Attempt purchase
        if producer_info['Connection'] == 'Socket':
            buy_product_socket(producer_info, name, desired)
        elif producer_info['Connection'] == 'REST':
            buy_product_rest(producer_info, name, desired)

        # Record subscription
        producer_name = producer_info["Name"]
        ip = producer_info["IP"]
        port = producer_info["PORT"]
        if producer_name not in purchased_subscriptions:
            purchased_subscriptions[producer_name] = {"ip": ip, "port": port, "products": []}
        purchased_subscriptions[producer_name]["products"].append({
            "name": name,
            "quantity": desired,
            "price": price
        })


# -----------------------------
# Subscriptions & resale fee
# -----------------------------

def list_subscriptions():
    if not purchased_subscriptions:
        print(f"{COLOR_ERROR}Error: {COLOR_RESET}You don't have any subscriptions.")
        return

    print("--- Subscriptions ---")
    for producer_name, data in purchased_subscriptions.items():
        ip = data["ip"]
        port = data["port"]
        print(f"\nProducer: {producer_name} (IP: {ip}, Port: {port})")
        for product in data["products"]:
            name = product["name"]
            qty = int(product["quantity"])
            buy_price = float(product["price"])
            fee_pct = float(resale_fees.get(name, DEFAULT_RESALE_FEE))
            fee_value = round(buy_price * fee_pct, 2)
            sell_price = buy_price + (fee_value / 100)
            print(f" - {name} - Quantity: {qty}")
            print(f"\tSale Price: {sell_price:.2f}€ ( Buy Price: {buy_price:.2f}€ | Resale Fee: {fee_pct}%)")


def set_resale_fee():
    try:
        print("\n--- Set Resale Fee ---")
        print("\nAvailable products:")
        product_id = 1
        flat = []
        for pinfo in purchased_subscriptions.values():
            for p in pinfo["products"]:
                print(f"{product_id}. Product: {p['name']} - Buy Price: {p['price']}")
                flat.append(p)
                product_id += 1
        if not flat:
            print("No products found in subscriptions.")
            return
        selection = int(input("\nEnter the number of the product to set the resale fee: "))
        if selection < 1 or selection > len(flat):
            print(f"{COLOR_ERROR}Error: {COLOR_RESET}Invalid product number.")
            return
        chosen = flat[selection - 1]
        print(f"You selected: {chosen['name']}")
        fee = float(input("Enter new resale fee (%): "))
        if fee < 0:
            print(f"{COLOR_ERROR}Error: {COLOR_RESET}Fee cannot be negative.")
            return
        resale_fees[chosen['name']] = fee
        print(f"{COLOR_SUCCESS}Success: {COLOR_RESET}Resale fee for '{chosen['name']}' set to {fee}%.")
    except ValueError:
        print(f"{COLOR_ERROR}Error: {COLOR_RESET}Invalid value. Enter a valid number.")


# -----------------------------
# Menu & main
# -----------------------------

def marketplace_menu():
    while True:
        print("--- Marketplace Menu ---")
        print("1. List Subscriptions")
        print("2. Buy Products")
        print("3. Set Resale Fee")
        print("99. Exit")
        choice = input("Choose an option: ")
        if choice == '1':
            list_subscriptions()
        elif choice == '2':
            main()
        elif choice == '3':
            set_resale_fee()
        elif choice == '99':
            print(f"{COLOR_SUCCESS}Success: {COLOR_RESET}Leaving the Marketplace. See you soon!")
            time.sleep(1)
            break
        else:
            print(f"{COLOR_ERROR}Error: {COLOR_RESET}Invalid option. Try again.")


def main():
    producers_with_category = []
    products_for_category = []

    available_categories = set()
    rest_categories = get_categories_rest()
    socket_categories = get_categories_socket()
    all_categories = rest_categories + socket_categories

    for producer in all_categories:
        available_categories.update(producer['Categories'])

    print("Available Categories:")
    print(", ".join(sorted(available_categories)) if available_categories else "(none)")

    chosen_category = input("Choose a category: ")

    for producer in all_categories:
        if chosen_category in producer['Categories']:
            producers_with_category.append(producer)

    for producer in producers_with_category:
        products = get_products_by_category(producer, chosen_category)
        producer_with_products = {
            'Name': producer['Name'],
            'IP': producer['IP'],
            'PORT': producer['PORT'],
            'Connection': producer['Connection'],
            'Products': []
        }
        for product in products:
            producer_with_products['Products'].append(product)
        products_for_category.append(producer_with_products)

    list_products(products_for_category)

    raw = input("\nEnter the numbers of the products you want to buy (comma-separated): ")
    try:
        chosen_ids = list(map(int, raw.split(','))) if raw.strip() else []
    except ValueError:
        print("Invalid input. Please enter valid numbers separated by commas.")
        return

    if chosen_ids:
        buy_products(products_for_category, chosen_ids)
    else:
        print("No products selected.")

    marketplace_menu()


if __name__ == "__main__":
    main()