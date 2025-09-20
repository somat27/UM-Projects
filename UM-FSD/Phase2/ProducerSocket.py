import socket
import random
import json
import threading
import os
import time
import psutil

lock = threading.RLock()

DEFAULT_IP = '127.0.0.1'
DEFAULT_PORT = 1025

server_active = True
producers_file = 'Data/Producers.json'
products_file = 'Data/Products.json'

ALLOWED_CATEGORIES = [
    "Fruit", "Books", "Clothing", "Tools", "Computers", "Smartphones", "Movies", "Shoes"
]

COLOR_SUCCESS = '\033[92m'
COLOR_ERROR = '\033[91m'
COLOR_RESET = '\033[0m'


def load_data(filepath):
    with lock:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []


def save_data(filepath, data):
    with lock:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)


def next_id_or_port_socket(items, key, default_value):
    values = [int(item[key]) for item in items if item.get(key) and str(item[key]).isdigit()]
    return max(values) + 1 if values else default_value


def register_producer(producer_name, default_ip):
    producers = load_data(producers_file)
    producer_id = next_id_or_port_socket(producers, 'ID', 1)
    socket_port = next_id_or_port_socket(producers, 'Port', DEFAULT_PORT)
    new_producer = {
        "ID": producer_id,
        "Name": producer_name,
        "IP": default_ip,
        "Port": socket_port,
        "Products": []
    }
    producers.append(new_producer)
    save_data(producers_file, producers)
    print(f"Producer '{producer_name}' registered with ID {producer_id} and Port {socket_port}.")
    return producer_id, socket_port


def generate_items_for_producer_socket(producer_id, num_items):
    products = load_data(products_file)
    producers = load_data(producers_file)
    all_products = [dict(product, Category=category) for category, product_list in products.items() for product in product_list]
    selected = random.sample(all_products, min(num_items, len(all_products)))
    producer = next((p for p in producers if p['ID'] == producer_id), None)
    if not producer:
        print(f"{COLOR_ERROR}Error: {COLOR_RESET}Producer with ID {producer_id} not found.")
        return
    with lock:
        for product in selected:
            generated_item = {
                "Name": product['ProductName'],
                "Category": product['Category'],
                "Price": round(random.uniform(product['Price'][0], product['Price'][1]), 2),
                "Quantity": random.randint(product['Quantity'][0], product['Quantity'][1])
            }
            producer['Products'].append(generated_item)
        save_data(producers_file, producers)
    print(f"{num_items} items generated.")


def list_products_socket(products):
    return [
        f"{product['Name']} - Category: {product.get('Category', 'Unknown')} - Price: {product['Price']:.2f} - Quantity: {product['Quantity']}"
        for product in products
    ]


def replenish_stock_periodically(producer_id):
    interval_seconds = 60
    while True:
        time.sleep(interval_seconds)
        producers = load_data(producers_file)
        producer = next((p for p in producers if p["ID"] == producer_id), None)
        if producer and producer['Products']:
            to_update_count = random.randint(1, len(producer['Products']))
            to_update = random.sample(producer['Products'], to_update_count)
            with lock:
                for product in to_update:
                    current = product.get('Quantity', 0)
                    max_qty = random.randint(100, 200)
                    new_qty = min(current + random.randint(5, 20), max_qty)
                    product['Quantity'] = new_qty
                    print(f"Stock for '{product['Name']}' updated to {new_qty} [Old: {current}].")
            save_data(producers_file, producers)


def list_products_endpoint(client_sock, producer_id):
    producers = load_data(producers_file)
    producer = next((p for p in producers if p['ID'] == producer_id), None)
    products = producer['Products'] if producer else []
    response = "\n".join(list_products_socket(products)) if products else "No products available."
    client_sock.sendall(response.encode('utf-8'))


def purchase_product_endpoint(client_sock, producer_id, product_name, quantity):
    producers = load_data(producers_file)
    producer = next((p for p in producers if p['ID'] == producer_id), None)
    with lock:
        info = next((prod for prod in (producer or {}).get('Products', []) if prod['Name'] == product_name), None)
        if info and info['Quantity'] >= quantity:
            info['Quantity'] -= quantity
            save_data(producers_file, producers)
            response = "OK"
            print(f"Client bought {quantity} of '{product_name}'.")
        else:
            response = "Product not found or insufficient quantity."
            print(f"Purchase failed: Product '{product_name}' not found or insufficient quantity.")
    client_sock.sendall(response.encode('utf-8'))


def list_categories(client_sock, producer_id):
    producers = load_data(producers_file)
    producer = next((p for p in producers if p['ID'] == producer_id), None)
    if producer:
        categories = {product.get('Category') for product in producer['Products'] if product.get('Category')}
        categories = list(categories)
        if categories:
            response = "Available categories:\n" + "\n".join(categories)
        else:
            response = "No categories available."
    else:
        response = f"Producer with ID {producer_id} not found."
    client_sock.sendall(response.encode('utf-8'))


def list_products_by_category(client_sock, producer_id, category):
    try:
        with open(producers_file, 'r', encoding='utf-8') as file:
            producers = json.load(file)
        producer = next((p for p in producers if p['ID'] == producer_id), None)
        if producer:
            found = []
            for product in producer['Products']:
                if product['Category'].strip().lower() == category.strip().lower():
                    info = {
                        "category": product['Category'],
                        "product": product['Name'],
                        "quantity": product['Quantity'],
                        "price": f"{product['Price']}"
                    }
                    found.append(info)
            if found:
                response = json.dumps(found, ensure_ascii=False)
            else:
                response = json.dumps({"error": f"No products in category {category} for producer {producer_id}."}, ensure_ascii=False)
        else:
            response = json.dumps({"error": f"Producer with ID {producer_id} not found."}, ensure_ascii=False)
        client_sock.sendall(response.encode('utf-8'))
    except Exception as e:
        print(f"Error listing products by category: {e}")
        client_sock.sendall(f"Error listing products: {e}".encode('utf-8'))


def handle_connection(client_sock, addr, connections, marketplace_products, producer_id):
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
                        print(f"List products in category: {category.strip()}")
                        list_products_by_category(client_sock, producer_id, category.strip())
                    except Exception as e:
                        print(f"Error processing LIST_PRODUCTS_CATEGORY: {e}")
                else:
                    if data.startswith("SUBSCRIBE_PRODUCT"):
                        try:
                            _, product_name, quantity = data.split(',', maxsplit=2)
                            quantity = int(quantity.strip())
                            marketplace_products.setdefault(addr, []).append((product_name.strip(), quantity))
                            purchase_product_endpoint(client_sock, producer_id, product_name.strip(), quantity)
                        except Exception as e:
                            print(f"Error processing SUBSCRIBE_PRODUCT: {e}")
                    elif data.startswith("LIST_PRODUCTS"):
                        list_products_endpoint(client_sock, producer_id)
                    elif data.startswith("HEARTBEAT"):
                        client_sock.sendall("OK".encode('utf-8'))
                    elif data.startswith("LIST_CATEGORIES"):
                        list_categories(client_sock, producer_id)
    except Exception as e:
        print(f"Connection error with {addr}: {e}")
    finally:
        print(f"Connection closed with {addr}.")
        client_sock.close()


def producer_server(producer_name, producer_id, port, ip):
    global server_active
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind(('', int(port)))
    server_sock.listen(5)
    print(f"Producer server '{producer_name}' started on IP {ip} and port {port}.")
    connections = []
    marketplace_products = {}
    threading.Thread(target=replenish_stock_periodically, args=(producer_id,), daemon=True).start()
    while server_active:
        try:
            server_sock.settimeout(1.0)
            try:
                client_sock, addr = server_sock.accept()
            except socket.timeout:
                continue
            threading.Thread(
                target=handle_connection,
                args=(client_sock, addr, connections, marketplace_products, producer_id),
                daemon=True
            ).start()
        except OSError:
            break
    server_sock.close()
    print(f"Producer server '{producer_name}' stopped.")


def login_producer():
    producer_name = input("Enter producer name: ")
    producer_id = input("Enter producer ID: ")
    producers = load_data(producers_file)
    producer = next((p for p in producers if p['Name'] == producer_name and str(p['ID']) == str(producer_id)), None)
    if producer:
        print(f"Welcome back, {producer['Name']}!")
        return producer['Name'], producer['ID'], producer['Port'], producer['IP']
    else:
        print("Producer not found.")
        return None, None, None, None


def main_menu(default_ip):
    while True:
        choice = input("\n--- Main Menu ---\n1. Create new producer\n2. Log in as existing producer\n99. Exit\nChoose an option: ")
        if choice == '1':
            producer_name = input("Enter new producer name: ")
            producer_id, port = register_producer(producer_name, default_ip)
            generate_items_for_producer_socket(producer_id, random.randint(3, 5))
            producer_server(producer_name, producer_id, port, default_ip)
            break
        elif choice == '2':
            producer_name, producer_id, port, ip = login_producer()
            if producer_name and producer_id:
                producer_server(producer_name, producer_id, port, ip)
            break
        elif choice == '99':
            print("Exiting...")
            break
        else:
            print("Invalid option. Try again.")


def get_vpn_ip():
    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET and addr.address.startswith('10.'):
                return addr.address
    return None


if __name__ == "__main__":
    ip_default = get_vpn_ip()
    if ip_default:
        print(f"{COLOR_SUCCESS}Success: {COLOR_RESET}VPN IP detected: {ip_default}")
        main_menu(ip_default)
    else:
        print(f"{COLOR_ERROR}Error: {COLOR_RESET}VPN IP not detected, try again!")