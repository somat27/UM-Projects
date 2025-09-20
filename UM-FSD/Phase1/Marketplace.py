import random
import socket
import json
import os
import time
import threading

Lock = threading.RLock()

PRODUCERS_FILE = 'Data/Producers.json'
PRODUCTS_FILE = 'Data/Products.json'

connections = {}
purchased_products = []
heartbeat_threads = {}
resale_rates = {}

default_rate = 20.0

def load_json(path):
    try:
        with open(path, 'r') as f:
            content = f.read()
            return json.loads(content)
    except FileNotFoundError:
        print(f"File {path} not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error decoding JSON file {path}.")
        return []

def choose_category():
    products = load_json(PRODUCTS_FILE)
    categories = list(products.keys())
    return random.choice(categories) if categories else None

def port_in_use(ip, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.01)
        try:
            s.bind((ip, port))
            return False
        except socket.error:
            return True

def get_active_producers():
    producers = load_json(PRODUCERS_FILE)
    return [
        (p["ID"], p["IP"], p["Port"], p["Name"])
        for p in producers if port_in_use(p["IP"], p["Port"])
    ]

def list_subscriptions():
    global default_rate
    per_producer = {}
    for producer_id, producer_name, ip, port, product_name, quantity, buy_price in purchased_products:
        if producer_id not in per_producer:
            per_producer[producer_id] = {
                "name": producer_name,
                "ip": ip,
                "port": port,
                "products": []
            }
        resale = resale_rates.get(product_name, default_rate)
        sell_price = buy_price + (buy_price * resale / 100)
        per_producer[producer_id]["products"].append((product_name, quantity, buy_price, resale, sell_price))
    for producer_id, details in per_producer.items():
        print(f"Producer: {details['name']} (ID: {producer_id}, IP: {details['ip']}, Port: {details['port']})")
        for product_name, quantity, buy_price, resale, sell_price in details["products"]:
            print(f"  - Name: {product_name}, Quantity: {quantity}, Buy Price: {buy_price:.2f}, Sell Price: {sell_price:.2f} ({resale}%)")

def set_resale_rate():
    if not purchased_products:
        print("No products purchased yet.")
        return
    print("Purchased products available for resale:")
    for i, (producer_id, producer_name, ip, port, product_name, quantity, buy_price) in enumerate(purchased_products, 1):
        current = resale_rates.get(product_name, 0)
        print(f"{i}. {product_name} - Quantity: {quantity}, Current Resale Rate: {current}% (Producer: {producer_name})")
    try:
        idx = int(input("\nChoose the product number to set the resale rate: "))
        chosen = purchased_products[idx - 1]
        rate = float(input(f"Enter the resale rate for {chosen[4]} (%): "))
        if rate < 0:
            print("Rate cannot be negative.")
            return
        resale_rates[chosen[4]] = rate
        print(f"Resale rate {rate}% set for product {chosen[4]}.")
    except (ValueError, IndexError):
        print("Invalid selection. Try again.")

def buy_products():
    products = load_json(PRODUCTS_FILE)
    categories = list(products.keys())
    if not categories:
        print("No categories available.")
        return
    print("Available categories:")
    for cat in categories:
        print(f"- {cat}")
    while True:
        category = input("Choose a Category (or 0 to go back): ")
        if category == '0':
            print("Returning to previous menu.")
            return
        if category in categories:
            if search_products_menu(category) != 1:
                break
            else:
                print(f"No products available in category {category}. Try again.")
        else:
            print("Invalid category. Try again.")

def connect_to_producer(old_sock, ip, port, producer_name):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        connections[(ip, port)] = (sock, producer_name)
        return sock
    except socket.error:
        return old_sock

def check_connection_periodically(sock, ip, port, producer_name, timeout=30):
    fails = 0
    while fails * 2 < timeout:
        with Lock:
            try:
                sock.sendall(b"HEARTBEAT")
                response = sock.recv(1024).decode('utf-8')
                if response != "OK":
                    raise socket.error("Unexpected producer response")
                fails = 0
            except socket.error:
                fails += 1
                print(f"Lost connection with producer {producer_name} ({ip}:{port}) - attempt {fails}")
                new_sock = connect_to_producer(sock, ip, port, producer_name)
                if new_sock and new_sock != sock:
                    print(f"Reconnected with producer {producer_name} ({ip}:{port})")
                    sock.close()
                    sock = new_sock
                    connections[(ip, port)] = (sock, producer_name)
        time.sleep(2)
    print(f"Producer {producer_name} ({ip}:{port}) disconnected for more than {timeout} seconds. Removing products.")
    remove_producer_products(producer_name, ip, port)
    return False

def remove_producer_products(producer_name, ip, port):
    global purchased_products
    global connections
    purchased_products = [p for p in purchased_products if p[1] != producer_name]
    if (ip, port) in connections:
        sock, _ = connections[(ip, port)]
        sock.close()
        del connections[(ip, port)]
    print(f"All products from producer {producer_name} were removed.")

def search_products_menu(selected_category):
    global connections
    global purchased_products
    global default_rate
    active = get_active_producers()
    product_list = []
    for _, ip, port, producer_name in active:
        sock_info = connections.get((ip, port))
        if sock_info is None:
            sock = connect_to_producer(None, ip, port, producer_name)
            if sock is None:
                continue
            thread_heartbeat = threading.Thread(target=check_connection_periodically, args=(sock, ip, port, producer_name))
            thread_heartbeat.daemon = True
            thread_heartbeat.start()
            heartbeat_threads[(ip, port)] = thread_heartbeat
        else:
            sock = sock_info[0]
        try:
            with Lock:
                sock.sendall(b"LIST_PRODUCTS")
                products = sock.recv(4096).decode('utf-8')
            filtered = [
                line for line in products.splitlines()
                if line.partition(' - ')[2].split('Category: ')[1].split(' - ')[0] == selected_category
                and int(line.partition('Quantity: ')[2]) > 0
            ]
            for product in filtered:
                product_list.append((producer_name, ip, port, product))
        except socket.error as e:
            print(f"Error requesting products from {producer_name} ({ip}:{port}): {e}")
            sock.close()
            connections.pop((ip, port), None)
    if not product_list:
        return 1
    print(f"\nCategory: {selected_category}")
    print("\nAvailable products:")
    prev_producer = None
    for i, (producer_name, ip, port, product) in enumerate(product_list, 1):
        if producer_name != prev_producer:
            print(f"Producer: {producer_name} (IP: {ip}, Port: {port})")
            prev_producer = producer_name
        print(f"{i}. {product}")
    selections = input("\nChoose the numbers of the products to buy (comma-separated): ")
    try:
        valid = [product_list[int(num.strip()) - 1] for num in selections.split(',') if num.strip().isdigit()]
        for producer_name, ip, port, product in valid:
            sock = connections[(ip, port)][0]
            product_name = product.split(' - ')[0]
            buy_price = float(product.split('Price: ')[1].split(' - ')[0])
            producer_id = next(p[0] for p in get_active_producers() if p[1] == ip and p[2] == port)
            while True:
                qty = input(f"Enter quantity for {product_name}: ")
                with Lock:
                    purchase_msg = f"SUBSCRIBE_PRODUCT,{product_name},{qty}"
                    sock.sendall(purchase_msg.encode('utf-8'))
                    response = sock.recv(1024).decode('utf-8')
                if response == "Product not found or insufficient quantity.":
                    print(response)
                else:
                    purchased_products.append((producer_id, producer_name, ip, port, product_name, qty, buy_price))
                    resale_rates[product_name] = default_rate
                    print(f"Purchase confirmed with default 20% resale rate for {product_name}.")
                    break
    except (ValueError, IndexError):
        print("Invalid selection. Try again with valid numbers.")


def marketplace_menu():
    while True:
        print("--- Marketplace Menu ---")
        print("1. Subscriptions List")
        print("2. Buy Products")
        print("3. Set Resale Rate")
        print("99. Exit")
        choice = input("Choose an option: ")
        if choice == '1':
            list_subscriptions()
        elif choice == '2':
            buy_products()
        elif choice == '3':
            set_resale_rate()
        elif choice == '99':
            print("Exiting Marketplace. Goodbye!")
            break
        else:
            print("Invalid option. Try again.")


def start():
    while True:
        category = choose_category()
        if search_products_menu(category) != 1:
            break
    marketplace_menu()
    for sock, _ in connections.values():
        sock.close()
    print("Connections closed.")

if __name__ == "__main__":
    start()
