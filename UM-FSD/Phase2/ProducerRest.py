import socket
import random
import json
import threading
import os
import platform
import logging
from flask import Flask, jsonify, request
import requests
import psutil
import time

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.CRITICAL)

lock = threading.RLock()

DEFAULT_IP = '127.0.0.1'
MANAGER_IP = '193.136.11.170'
DEFAULT_PORT = 1025
MANAGER_PORT = 5001
SERVER_ACTIVE = True
PRODUCER_INFO = {}
PRODUCTS_FILE = 'Data/Products.json'
ALLOWED_CATEGORIES = [
    "Fruit", "Books", "Clothing", "Tools", "Computers", "Smartphones", "Movies", "Shoes"
]
REST_NOTIFICATIONS = []

COLOR_SUCCESS = '\033[92m'
COLOR_ERROR = '\033[91m'
COLOR_RESET = '\033[0m'

def clear_terminal():
    system = platform.system()
    if system == 'Windows':
        os.system('cls')
    else:
        os.system('clear')

def get_vpn_ip():
    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET and addr.address.startswith('10.'):
                return addr.address
    return None

def load_data(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def is_port_in_use(ip, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.01)
        result = s.connect_ex((ip, port))
        return result == 0

def find_available_port(ip, port):
    while True:
        if not is_port_in_use(ip, port):
            return port
        port += 1

def register_producer(producer_name):
    global PRODUCER_INFO, DEFAULT_IP, DEFAULT_PORT, COLOR_SUCCESS, COLOR_ERROR, COLOR_RESET
    if not DEFAULT_IP or not DEFAULT_PORT:
        print(f"{COLOR_ERROR}Error: {COLOR_RESET}Default IP or Port not set.")
        return None

    port = find_available_port(DEFAULT_IP, DEFAULT_PORT)
    PRODUCER_INFO = {
        "Name": producer_name,
        "IP": DEFAULT_IP,
        "Port": port,
        "Products": []
    }

    post_payload = {
        "ip": PRODUCER_INFO["IP"],
        "port": PRODUCER_INFO["Port"],
        "name": PRODUCER_INFO["Name"]
    }

    try:
        url = f'http://{MANAGER_IP}:{MANAGER_PORT}/producer'
        response = requests.post(url, json=post_payload)
        if response.status_code == 200:
            print(f"{COLOR_SUCCESS}Success: {COLOR_RESET}Producer info updated successfully.")
        elif response.status_code == 201:
            print(f"{COLOR_SUCCESS}Success: {COLOR_RESET}New producer registered successfully.")
        elif response.status_code == 400:
            print(f"{COLOR_ERROR}Error: {COLOR_RESET}Bad request. The server could not process it.")
        else:
            print(f"{COLOR_ERROR}Unexpected error: {COLOR_RESET}Status code {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"{COLOR_ERROR}Connection error: {COLOR_RESET}{e}")

    return PRODUCER_INFO

def generate_items_for_producer(producer_info, num_items):
    products_data = load_data(PRODUCTS_FILE)
    all_products = [dict(product, Category=category) for category, product_list in products_data.items() for product in product_list]
    selected_products = random.sample(all_products, min(num_items, len(all_products)))

    for product in selected_products:
        price = random.uniform(product['Price'][0], product['Price'][1])
        quantity = random.randint(product['Quantity'][0], product['Quantity'][1])
        generated_item = {
            "Name": product['ProductName'],
            "Category": product['Category'],
            "Price": round(price, 2),
            "Quantity": quantity
        }
        producer_info['Products'].append(generated_item)

    print(f"{COLOR_SUCCESS}Success: {COLOR_RESET}{num_items} items generated for producer '{producer_info['Name']}'.")

def list_products():
    clear_terminal()
    if PRODUCER_INFO.get("Products"):
        print("--- Marketplace Products ---")
        for i, product in enumerate(PRODUCER_INFO["Products"], start=1):
            print(f"Product: {product['Name']}, Category: {product['Category']}, Quantity: {product['Quantity']}, Price: {product['Price']:.2f}")
    else:
        print("No products registered.")

def product_management_menu():
    global SERVER_ACTIVE
    while SERVER_ACTIVE:
        clear_terminal()
        print("--- Product Management Menu ---")
        print("1. Add product")
        print("2. Update product stock")
        print("3. Remove product")
        print("4. List products")
        print("5. Flask notifications")
        print("0. Exit management menu")
        option = input("Choose an option: ")

        if option == '1':
            product_name = input("Product name: ")
            print("Choose a category:")
            for i, category in enumerate(ALLOWED_CATEGORIES, 1):
                print(f"{i}. {category}")
            try:
                category_index = int(input("Category number: ")) - 1
                if 0 <= category_index < len(ALLOWED_CATEGORIES):
                    category = ALLOWED_CATEGORIES[category_index]
                else:
                    print(f"{COLOR_ERROR}Error: {COLOR_RESET}Invalid category.")
                    continue
            except ValueError:
                print(f"{COLOR_ERROR}Error: {COLOR_RESET}Invalid input. Please select a number.")
                continue
            price = float(input("Product price: "))
            quantity = int(input("Quantity in stock: "))
            PRODUCER_INFO["Products"].append({
                "Name": product_name,
                "Category": category,
                "Price": price,
                "Quantity": quantity
            })
            print(f"{COLOR_SUCCESS}Success: {COLOR_RESET}Product '{product_name}' added in category '{category}' with {quantity} in stock at {price:.2f}.")

        elif option == '2':
            list_products()
            product_name = input("Product name to update: ")
            found = False
            for product in PRODUCER_INFO["Products"]:
                if product["Name"] == product_name:
                    quantity = int(input("New quantity in stock: "))
                    product["Quantity"] = quantity
                    print(f"{COLOR_SUCCESS}Success: {COLOR_RESET}Stock for product '{product_name}' updated to {quantity}.")
                    found = True
                    break
            if not found:
                print(f"{COLOR_ERROR}Error: {COLOR_RESET}Product '{product_name}' not found.")

        elif option == '3':
            list_products()
            product_name = input("Product name to remove: ")
            found = False
            for product in list(PRODUCER_INFO["Products"]):
                if product["Name"] == product_name:
                    PRODUCER_INFO["Products"].remove(product)
                    print(f"{COLOR_SUCCESS}Success: {COLOR_RESET}Product '{product_name}' removed.")
                    found = True
                    break
            if not found:
                print(f"{COLOR_ERROR}Error: {COLOR_RESET}Product '{product_name}' not found.")

        elif option == '4':
            list_products()
            input("\nPress Enter to return to the main menu...")

        elif option == '5':
            notifications_menu()

        elif option == '0':
            print("Exiting management menu and shutting down the server...")
            SERVER_ACTIVE = False
            break
        else:
            print(f"{COLOR_ERROR}Error: {COLOR_RESET}Invalid option.")

    time.sleep(1)
    print("Shutting down the server. Please wait...")
    time.sleep(1)
    print("Server shut down successfully.")

def start_flask_server():
    app.run(host=PRODUCER_INFO["IP"], port=PRODUCER_INFO["Port"], debug=False, use_reloader=False)

def notifications_menu():
    clear_terminal()
    global REST_NOTIFICATIONS
    print("--- Flask Notifications ---")
    if REST_NOTIFICATIONS:
        for msg in REST_NOTIFICATIONS:
            print(f"- {msg}")
    else:
        print("No notifications available.")
    input("\nPress Enter to return to the main menu...")

def initial_menu():
    global PRODUCER_INFO
    while True:
        producer_name = input("Enter the producer name: ")
        PRODUCER_INFO = register_producer(producer_name)
        generate_items_for_producer(PRODUCER_INFO, random.randint(3, 5))
        threading.Thread(target=start_flask_server).start()
        time.sleep(3)
        threading.Thread(target=product_management_menu).start()
        break

def add_notification(message):
    client_ip = request.remote_addr
    client_port = request.host.split(':')[-1]
    full_notification = f"{message} (IP: {client_ip}, Port: {client_port})"
    REST_NOTIFICATIONS.append(full_notification)

@app.route('/categories', methods=['GET'])
def get_categories():
    if "Products" in PRODUCER_INFO and PRODUCER_INFO["Products"]:
        available_categories = set()
        for product in PRODUCER_INFO["Products"]:
            category = product.get('Category')
            if category:
                available_categories.add(category)
        add_notification("Categories retrieved successfully.")
        return jsonify(list(available_categories)), 200
    else:
        add_notification("No registered products to get categories from.")
        return jsonify([]), 200

@app.route('/products', methods=['GET'])
def get_products_by_category():
    category = request.args.get('category')
    if not category:
        add_notification("Parameter 'category' not provided.")
        return jsonify({"error": "Parameter 'category' not provided"}), 400

    found_products = [
        product for product in PRODUCER_INFO.get("Products", [])
        if product.get('Category') == category
    ]

    if found_products:
        add_notification(f"Products found for category '{category}'.")
        return jsonify([
            {
                "category": product["Category"],
                "product": product["Name"],
                "quantity": product["Quantity"],
                "price": product["Price"]
            } for product in found_products
        ]), 200
    else:
        add_notification(f"No products found in category '{category}'.")
        return jsonify({"error": "Nonexistent category"}), 404

@app.route('/buy/<product>/<int:quantity>', methods=['GET'])
def buy_product(product, quantity):
    with lock:
        product_info = next((p for p in PRODUCER_INFO['Products'] if p['Name'] == product), None)
        if product_info:
            if product_info["Quantity"] >= quantity:
                unit_price = product_info["Price"]
                total_price = unit_price * quantity
                product_info["Quantity"] -= quantity
                add_notification(f"{quantity} units of '{product}' purchased for {total_price:.2f}€.")
                return jsonify({
                    "success": f"{quantity} units of {product} purchased",
                    "unit_price": unit_price,
                    "total_price": total_price
                }), 200
            else:
                add_notification(f"Insufficient quantity for '{product}'.")
                return jsonify({"error": "Insufficient quantity"}), 404
        else:
            add_notification(f"Product '{product}' not found.")
            return jsonify({"error": "Product not found"}), 404

if __name__ == "__main__":
    DEFAULT_IP = get_vpn_ip()
    if DEFAULT_IP:
        print(f"{COLOR_SUCCESS}Success: {COLOR_RESET}VPN IP detected: {DEFAULT_IP}")
        initial_menu()
    else:
        print(f"{COLOR_ERROR}Error: {COLOR_RESET}VPN IP not detected, please try again!")
