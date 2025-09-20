# ------------ Imports ------------ #
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
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
# ------------ Imports ------------ #

# ------------ Global Config ------------ #
app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.CRITICAL)

Lock = threading.RLock()

DEFAULT_IP = '127.0.0.1'
DEFAULT_PORT_SOCKET = 1025
DEFAULT_PORT_REST = 2025

SOCKET_SERVER_ACTIVE = True
REST_SERVER_ACTIVE = True

ProducerInfo = {}
producers_file = 'Data/Producers.json'
products_file = 'Data/Products.json'

ALLOWED_CATEGORIES = ["Fruit", "Books", "Clothing", "Tools", "Computers", "Smartphones", "Movies", "Shoes"]

REST_NOTIFICATIONS = []

COLOR_SUCCESS = '\033[92m'
COLOR_ERROR = '\033[91m'
COLOR_RESET = '\033[0m'
COLOR_DEBUG = '\033[94m'
DEBUG = False
# ------------ Global Config ------------ #

def dprint(msg):
    if DEBUG:
        print(f"{COLOR_DEBUG}DEBUG: {COLOR_RESET}{msg}")

# ------------ REST Routes (English) ------------ #
@app.route('/categories', methods=['GET'])
def get_categories():
    if "Products" in ProducerInfo and ProducerInfo["Products"]:
        cats = sorted({p.get('Category') for p in ProducerInfo["Products"] if p.get('Category')})
        add_notification("Categories fetched successfully.")
        return jsonify(cats), 200
    else:
        add_notification("No products registered to fetch categories from.")
        return jsonify([]), 200

@app.route('/products', methods=['GET'])
def get_products_by_category():
    category = request.args.get('category')
    if not category:
        add_notification("Missing 'category' parameter.")
        return jsonify({"error": "Missing 'category' parameter"}), 400

    found = [p for p in ProducerInfo.get("Products", []) if p.get('Category') == category]
    if found:
        add_notification(f"Products found for category '{category}'.")
        return jsonify([
            {
                "category": p["Category"],
                "product": p["Name"],
                "quantity": p["Quantity"],
                "price": p["Price"]
            } for p in found
        ]), 200
    else:
        add_notification(f"No products in category '{category}'.")
        return jsonify({"error": "Nonexistent category"}), 404

@app.route('/buy/<product>/<int:quantity>', methods=['GET'])
def buy_product(product, quantity):
    with Lock:
        info = next((p for p in ProducerInfo.get('Products', []) if p['Name'] == product), None)
        if info:
            if info["Quantity"] >= quantity:
                unit = info["Price"]
                total = unit * quantity
                info["Quantity"] -= quantity
                add_notification(f"{quantity} units of '{product}' purchased for {total:.2f}€.")
                return jsonify({"success": f"{quantity} units of {product} purchased",
                                "unit_price": unit, "total_price": total}), 200
            else:
                add_notification(f"Insufficient quantity for '{product}'.")
                return jsonify({"error": "Insufficient quantity"}), 404
        else:
            add_notification(f"Product '{product}' not found.")
            return jsonify({"error": "Product not found"}), 404

@app.route('/secure/categories', methods=['GET'])
def secure_categories():
    try:
        categories = sorted({p['Category'] for p in ProducerInfo.get("Products", [])})
        signature = sign_message(categories)
        cert_path = "certificate.pem"
        if not os.path.exists(cert_path):
            raise FileNotFoundError(f"Certificate not found at {cert_path}")
        certificate = open(cert_path, "r").read()
        return jsonify({"message": categories,
                        "signature": signature.decode('cp437'),
                        "certificate": certificate}), 200
    except Exception as e:
        logging.error(f"/secure/categories error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/secure/products', methods=['GET'])
def secure_products():
    try:
        category = request.args.get('category')
        products = [{
            "category": p['Category'],
            "price": p['Price'],
            "product": p['Name'],
            "quantity": p['Quantity']
        } for p in ProducerInfo.get("Products", []) if p['Category'] == category]
        signature = sign_message(products)
        cert_path = "certificate.pem"
        if not os.path.exists(cert_path):
            raise FileNotFoundError(f"Certificate not found at {cert_path}")
        certificate = open(cert_path, "r").read()
        return jsonify({"message": products,
                        "signature": signature.decode('cp437'),
                        "certificate": certificate}), 200 if products else 404
    except Exception as e:
        logging.error(f"/secure/products error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/secure/buy/<product>/<int:quantity>', methods=['POST'])
def secure_buy(product, quantity):
    with Lock:
        cert_path = "certificate.pem"
        if not os.path.exists(cert_path):
            raise FileNotFoundError(f"Certificate not found at {cert_path}")
        certificate = open(cert_path, "r").read()

        info = next((p for p in ProducerInfo.get("Products", []) if p["Name"] == product), None)
        if info and info["Quantity"] >= quantity:
            info["Quantity"] -= quantity
            message = f"{quantity} units of {product} purchased successfully."
            signature = sign_message(message)
            return jsonify({"message": message,
                            "signature": signature.decode('cp437'),
                            "certificate": certificate}), 200
        else:
            message = "Insufficient quantity or product not found."
            signature = sign_message(message)
            return jsonify({"message": message,
                            "signature": signature.decode('cp437'),
                            "certificate": certificate}), 404
# ------------ REST Routes ------------ #

# ------------ REST Producer registration (manager) ------------ #
def register_secure_producer_forever(producer_name):
    # post to manager in PT keys for compatibility
    while True:
        try:
            r = requests.post(f'http://{ "193.136.11.170" }:5001/produtor_certificado', json={
                "ip": ProducerInfo["IP"],
                "porta": ProducerInfo["Port"],
                "nome": producer_name,
                "pubKey": open("public_key.pem", "r").read()
            })
            if r.status_code in (200, 201):
                cert = r.text
                with open("certificate.pem", "w") as f:
                    f.write(cert)
                add_notification("Certificate received and saved.")
            else:
                print(f"Register error: {r.status_code} - {r.text}")
        except requests.exceptions.RequestException as e:
            dprint(f"Register secure error: {e}")
        time.sleep(60)

def register_insecure_producer_forever(producer_name):
    while True:
        try:
            r = requests.post(f'http://{ "193.136.11.170" }:5001/produtor', json={
                "ip": ProducerInfo["IP"],
                "porta": ProducerInfo["Port"],
                "nome": producer_name
            })
            if r.status_code in (200, 201):
                add_notification(f"Producer '{producer_name}' registered (insecure).")
            else:
                print(f"Insecure register error: {r.status_code} - {r.text}")
        except requests.exceptions.RequestException as e:
            dprint(f"Register insecure error: {e}")
        time.sleep(60)

def sign_message(message):
    with open("private_key.pem", "rb") as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)
    if isinstance(message, (list, dict)):
        message = json.dumps(message).encode('utf-8')
    elif isinstance(message, str):
        message = message.encode('utf-8')
    sig = private_key.sign(
        message,
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256()
    )
    return sig

def generate_rsa_keys():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    with open("private_key.pem", "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ))
    with open("public_key.pem", "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ))
    return private_key, public_key

def register_secure_rest_producer(producer_name):
    global ProducerInfo, DEFAULT_IP, DEFAULT_PORT_REST
    private_key, public_key = generate_rsa_keys()
    port = next_free_port(DEFAULT_IP, DEFAULT_PORT_REST)
    ProducerInfo = {"Name": producer_name, "IP": DEFAULT_IP, "Port": port, "Products": []}

    payload = {
        "ip": ProducerInfo["IP"],             # manager expects PT keys
        "porta": ProducerInfo["Port"],
        "nome": ProducerInfo["Name"],
        "pubKey": public_key.public_bytes(encoding=serialization.Encoding.PEM,
                                          format=serialization.PublicFormat.SubjectPublicKeyInfo).decode('utf-8')
    }
    try:
        r = requests.post(f'http://{ "193.136.11.170" }:5001/produtor_certificado', json=payload)
        if r.status_code in (200, 201):
            cert = r.text
            with open("certificate.pem", "w") as f:
                f.write(cert)
            print("Certificate received and saved.")
        else:
            print(f"Register error: {r.status_code} - {r.text}")
    except requests.exceptions.RequestException as e:
        dprint(f"Connection error: {e}")
        return None
    return ProducerInfo

def register_insecure_rest_producer(producer_name):
    global ProducerInfo, DEFAULT_IP, DEFAULT_PORT_REST
    port = next_free_port(DEFAULT_IP, DEFAULT_PORT_REST)
    ProducerInfo = {"Name": producer_name, "IP": DEFAULT_IP, "Port": port, "Products": []}
    payload = {"ip": ProducerInfo["IP"], "porta": ProducerInfo["Port"], "nome": ProducerInfo["Name"]}
    try:
        r = requests.post(f'http://{ "193.136.11.170" }:5001/produtor', json=payload)
        if r.status_code in (200, 201):
            print("Insecure REST producer registered.")
        else:
            print(f"Insecure register error: {r.status_code} - {r.text}")
    except requests.exceptions.RequestException as e:
        dprint(f"Connection error: {e}")
        return None
    return ProducerInfo

def generate_items_for_rest(producer_info, n):
    data = load_data(products_file)
    all_products = [dict(prod, Category=cat) for cat, items in data.items() for prod in items]
    selected = random.sample(all_products, min(n, len(all_products)))
    for prod in selected:
        price = random.uniform(prod['Price'][0], prod['Price'][1])
        qty = random.randint(prod['Quantity'][0], prod['Quantity'][1])
        item = {"Name": prod['ProductName'], "Category": prod['Category'], "Price": round(price, 2), "Quantity": qty}
        producer_info['Products'].append(item)
    print(f"{COLOR_SUCCESS}Success: {COLOR_RESET}{n} item(s) generated for producer '{producer_info['Name']}'.")

def start_flask():
    app.run(host=ProducerInfo["IP"], port=ProducerInfo["Port"], debug=False, use_reloader=False)

def product_management_menu():
    global REST_SERVER_ACTIVE
    while REST_SERVER_ACTIVE:
        clear_terminal()
        print("--- Product Management ---")
        print("1. Add product")
        print("2. Update stock")
        print("3. Remove product")
        print("4. List products")
        print("5. Flask notifications")
        print("0. Exit")
        opt = input("Choose an option: ").strip()
        if opt == '1':
            name = input("Product name: ")
            print("Choose a category:")
            for i, c in enumerate(ALLOWED_CATEGORIES, 1):
                print(f"{i}. {c}")
            try:
                idx = int(input("Category number: ")) - 1
                if 0 <= idx < len(ALLOWED_CATEGORIES):
                    category = ALLOWED_CATEGORIES[idx]
                else:
                    print(f"{COLOR_ERROR}Error: {COLOR_RESET}Invalid category.")
                    continue
            except ValueError:
                print(f"{COLOR_ERROR}Error: {COLOR_RESET}Invalid number.")
                continue
            price = float(input("Price: "))
            qty = int(input("Quantity in stock: "))
            with Lock:
                ProducerInfo["Products"].append({"Name": name, "Category": category, "Price": price, "Quantity": qty})
            print(f"{COLOR_SUCCESS}Success: {COLOR_RESET}Added '{name}' in '{category}' with {qty} units at {price:.2f}.")
        elif opt == '2':
            list_products_rest()
            name = input("Product name to update: ")
            found = False
            for p in ProducerInfo["Products"]:
                if p["Name"] == name:
                    qty = int(input("New quantity: "))
                    p["Quantity"] = qty
                    print(f"{COLOR_SUCCESS}Success: {COLOR_RESET}Stock for '{name}' updated to {qty}.")
                    found = True
                    break
            if not found:
                print(f"{COLOR_ERROR}Error: {COLOR_RESET}Product '{name}' not found.")
        elif opt == '3':
            list_products_rest()
            name = input("Product name to remove: ")
            found = False
            for p in list(ProducerInfo["Products"]):
                if p["Name"] == name:
                    ProducerInfo["Products"].remove(p)
                    print(f"{COLOR_SUCCESS}Success: {COLOR_RESET}Product '{name}' removed.")
                    found = True
                    break
            if not found:
                print(f"{COLOR_ERROR}Error: {COLOR_RESET}Product '{name}' not found.")
        elif opt == '4':
            list_products_rest()
            input("\nPress Enter to go back...")
        elif opt == '5':
            notifications_menu()
        elif opt == '0':
            print("Shutting down server...")
            REST_SERVER_ACTIVE = False
            break
        else:
            print(f"{COLOR_ERROR}Error: {COLOR_RESET}Invalid option.")
    time.sleep(1)
    print("Server stopped.")
    os._exit(0)
# ------------ REST Producer registration ------------ #

# ------------ Socket Producer ------------ #
def socket_main_menu(default_ip):
    while True:
        opt = input("\n--- Initial Menu ---\n1. Create new producer\n2. Log in\n99. Exit\nChoose an option: ")
        if opt == '1':
            name = input("New producer name: ")
            pid, port = register_socket_producer(name, default_ip)
            generate_items_for_socket(pid, random.randint(3, 5))
            producer_socket_server(name, pid, port, default_ip)
            break
        elif opt == '2':
            name, pid, port, ip = login_producer()
            if name and pid:
                producer_socket_server(name, pid, port, ip)
            break
        elif opt == '99':
            print("Exiting...")
            break

def save_data(path, data):
    with Lock:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

def next_id_or_port(items, key, default_value):
    values = [int(item.get(key)) for item in items if str(item.get(key, "")).isdigit()]
    return max(values) + 1 if values else default_value

def register_socket_producer(name, default_ip):
    producers = load_data(producers_file)
    pid = next_id_or_port(producers, 'ID', 1)
    port = next_id_or_port(producers, 'Port', DEFAULT_PORT_SOCKET)
    new_p = {"ID": pid, "Name": name, "IP": default_ip, "Port": port, "Products": []}
    producers.append(new_p)
    save_data(producers_file, producers)
    print(f"Producer '{name}' registered with ID {pid} and Port {port}.")
    return pid, port

def generate_items_for_socket(pid, n):
    products = load_data(products_file)
    producers = load_data(producers_file)
    all_products = [dict(prod, Category=cat) for cat, items in products.items() for prod in items]
    selected = random.sample(all_products, min(n, len(all_products)))
    producer = next((p for p in producers if p['ID'] == pid), None)
    with Lock:
        for prod in selected:
            item = {
                "Name": prod['ProductName'],
                "Category": prod['Category'],
                "Price": round(random.uniform(prod['Price'][0], prod['Price'][1]), 2),
                "Quantity": random.randint(prod['Quantity'][0], prod['Quantity'][1])
            }
            producer['Products'].append(item)
        save_data(producers_file, producers)
    print(f"{n} items generated.")

def list_products_socket(products):
    return [
        f"{p['Name']} - Category: {p.get('Category','Unknown')} - Price: {p['Price']:.2f} - Quantity: {p['Quantity']}"
        for p in products
    ]

def replenish_stock_periodically(pid):
    interval = 60
    while True:
        time.sleep(interval)
        producers = load_data(producers_file)
        producer = next((p for p in producers if p["ID"] == pid), None)
        if producer and producer['Products']:
            to_update = random.sample(producer['Products'], random.randint(1, len(producer['Products'])))
            with Lock:
                for p in to_update:
                    current = p.get('Quantity', 0)
                    max_qty = random.randint(100, 200)
                    new_qty = min(current + random.randint(5, 20), max_qty)
                    p['Quantity'] = new_qty
                    print(f"Stock for '{p['Name']}' updated to {new_qty} [Old: {current}].")
            save_data(producers_file, producers)

def list_products_endpoint(client_sock, pid):
    producers = load_data(producers_file)
    producer = next((p for p in producers if p['ID'] == pid), None)
    products = producer['Products'] if producer else []
    resp = "\n".join(list_products_socket(products)) if products else "No products available."
    client_sock.sendall(resp.encode('utf-8'))

def buy_product_endpoint(client_sock, pid, product_name, quantity):
    producers = load_data(producers_file)
    producer = next((p for p in producers if p['ID'] == pid), None)
    with Lock:
        info = next((prod for prod in producer['Products'] if prod['Name'] == product_name), None)
        if info and info['Quantity'] >= quantity:
            info['Quantity'] -= quantity
            save_data(producers_file, producers)
            reply = "OK"
            print(f"Client bought {quantity} of '{product_name}'.")
        else:
            reply = "Product not found or insufficient quantity."
            print(f"Purchase failed for '{product_name}'.")
    client_sock.sendall(reply.encode('utf-8'))

def list_categories_socket(client_sock, pid):
    producers = load_data(producers_file)
    producer = next((p for p in producers if p['ID'] == pid), None)
    if producer:
        cats = sorted({prod['Category'] for prod in producer['Products']})
        reply = "Available categories:\n" + "\n".join(cats) if cats else "No categories available."
    else:
        reply = f"Producer with ID {pid} not found."
    client_sock.sendall(reply.encode('utf-8'))

def list_products_by_category_socket(client_sock, pid, category):
    try:
        with open(producers_file, 'r', encoding='utf-8') as f:
            producers = json.load(f)
        producer = next((p for p in producers if p['ID'] == pid), None)
        if producer:
            found = []
            for prod in producer['Products']:
                if prod['Category'].strip().lower() == category.strip().lower():
                    found.append({
                        "category": prod['Category'],
                        "product": prod['Name'],
                        "quantity": prod['Quantity'],
                        "price": f"{prod['Price']}"
                    })
            reply = json.dumps(found, ensure_ascii=False) if found else json.dumps({"error": f"No products in {category} for producer {pid}."}, ensure_ascii=False)
        else:
            reply = json.dumps({"error": f"Producer with ID {pid} not found."}, ensure_ascii=False)
        client_sock.sendall(reply.encode('utf-8'))
    except Exception as e:
        dprint(f"list_products_by_category_socket error: {e}")
        client_sock.sendall(f"Error: {e}".encode('utf-8'))

def handle_socket_connection(client_sock, addr, connections, marketplace_products, pid):
    try:
        print(f"Connection established with {addr}.")
        with client_sock:
            while True:
                data = client_sock.recv(1024).decode('utf-8')
                if not data:
                    break
                print(f"Message received: {data}")
                if data.startswith("LIST_PRODUCTS_CATEGORY"):
                    try:
                        _, category = data.split(",", maxsplit=1)
                        list_products_by_category_socket(client_sock, pid, category.strip())
                    except Exception as e:
                        dprint(f"Error LIST_PRODUCTS_CATEGORY: {e}")
                else:
                    if data.startswith("SUBSCRIBE_PRODUCT"):
                        try:
                            _, product_name, qty = data.split(',', maxsplit=2)
                            qty = int(qty.strip())
                            marketplace_products.setdefault(addr, []).append((product_name.strip(), qty))
                            buy_product_endpoint(client_sock, pid, product_name.strip(), qty)
                        except Exception as e:
                            dprint(f"Error SUBSCRIBE_PRODUCT: {e}")
                    elif data.startswith("LIST_PRODUCTS"):
                        list_products_endpoint(client_sock, pid)
                    elif data.startswith("HEARTBEAT"):
                        client_sock.sendall("OK".encode('utf-8'))
                    elif data.startswith("LIST_CATEGORIES"):
                        list_categories_socket(client_sock, pid)
    except Exception as e:
        dprint(f"Socket connection error {addr}: {e}")
    finally:
        print(f"Connection closed {addr}.")
        client_sock.close()

def producer_socket_server(producer_name, pid, port, ip):
    global SOCKET_SERVER_ACTIVE
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind(('', int(port)))
    server_sock.listen(5)
    print(f"Producer socket server '{producer_name}' on {ip}:{port}")
    connections = []
    marketplace_products = {}
    threading.Thread(target=replenish_stock_periodically, args=(pid,), daemon=True).start()
    while SOCKET_SERVER_ACTIVE:
        try:
            server_sock.settimeout(1.0)
            try:
                client_sock, addr = server_sock.accept()
            except socket.timeout:
                continue
            threading.Thread(target=handle_socket_connection, args=(client_sock, addr, connections, marketplace_products, pid), daemon=True).start()
        except OSError:
            break
    server_sock.close()
    print(f"Producer socket server '{producer_name}' stopped.")
# ------------ Socket Producer ------------ #

# ------------ Common Utilities ------------ #
def clear_terminal():
    system = platform.system()
    os.system('cls' if system == 'Windows' else 'clear')

def next_free_port(ip, port):
    while True:
        if not is_port_in_use(ip, port):
            return port
        port += 1

def is_port_in_use(ip, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.01)
        return s.connect_ex((ip, int(port))) == 0

def list_products_rest():
    clear_terminal()
    if ProducerInfo.get("Products"):
        print("--- Marketplace Products ---")
        for i, p in enumerate(ProducerInfo["Products"], start=1):
            print(f"Product: {p['Name']}, Category: {p['Category']}, Quantity: {p['Quantity']}, Price: {p['Price']:.2f}")
    else:
        print("No products registered.")

def notifications_menu():
    clear_terminal()
    global REST_NOTIFICATIONS
    print("--- Flask Notifications ---")
    if REST_NOTIFICATIONS:
        for msg in REST_NOTIFICATIONS:
            print(f"- {msg}")
    else:
        print("No notifications.")
    input("\nPress Enter to go back...")

def add_notification(message):
    try:
        if request and request.remote_addr:
            ip_client = request.remote_addr
            port_client = request.host.split(':')[-1]
            full = f"{message} (IP: {ip_client}, Port: {port_client})"
        else:
            full = message
        REST_NOTIFICATIONS.append(full)
    except RuntimeError:
        REST_NOTIFICATIONS.append(message)

def load_data(path):
    with Lock:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

def get_vpn_ip():
    for _, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET and addr.address.startswith('10.'):
                return addr.address
    return None

def main_menu(default_ip):
    while True:
        print("\nChoose producer type to start:")
        print("1. Secure REST Producer")
        print("2. Insecure REST Producer")
        print("3. Socket Producer")
        print("4. Exit")
        choice = input("Option: ").strip()
        if choice == "1":
            while True:
                name = input("Secure REST producer name: ")
                info = register_secure_rest_producer(name)
                generate_items_for_rest(info, random.randint(3, 5))
                threading.Thread(target=register_secure_producer_forever, args=(name,), daemon=True).start()
                threading.Thread(target=start_flask).start()
                time.sleep(3)
                threading.Thread(target=product_management_menu).start()
                break
        elif choice == "2":
            while True:
                name = input("Insecure REST producer name: ")
                info = register_insecure_rest_producer(name)
                generate_items_for_rest(info, random.randint(3, 5))
                threading.Thread(target=register_insecure_producer_forever, args=(name,), daemon=True).start()
                threading.Thread(target=start_flask).start()
                time.sleep(3)
                threading.Thread(target=product_management_menu).start()
                break
        elif choice == "3":
            socket_main_menu(default_ip)
            break
        elif choice == "4":
            print("Goodbye.")
            break
        else:
            print("Invalid option. Try again.")
# ------------ Common Utilities ------------ #

if __name__ == "__main__":
    ip_default = get_vpn_ip()
    if ip_default:
        print(f"{COLOR_SUCCESS}Success: {COLOR_RESET}VPN IP detected: {ip_default}")
        main_menu(ip_default)
    else:
        print(f"{COLOR_ERROR}Error: {COLOR_RESET}VPN IP not detected, please try again!")