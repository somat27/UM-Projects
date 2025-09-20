import socket
import random
import json
import threading
import os
import time

Lock = threading.RLock()

IP = '127.0.0.1'
DEFAULT_PORT = 1025

server_active = True
producers_file = 'Data/Producers.json'
products_file = 'Data/Products.json'

def load_data(path):
    with Lock:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

def save_data(path, data):
    with Lock:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

def next_id_or_port(items, key, default_value):
    values = [int(item[key]) for item in items if item.get(key) and str(item[key]).isdigit()]
    return max(values) + 1 if values else default_value

def register_producer(producer_name):
    producers = load_data(producers_file)
    producer_id = next_id_or_port(producers, 'ID', 1)
    socket_port = next_id_or_port(producers, 'Port', DEFAULT_PORT)
    new_producer = {"ID": producer_id, "Name": producer_name, "IP": IP, "Port": socket_port, "Products": []}
    producers.append(new_producer)
    save_data(producers_file, producers)
    print(f"Producer '{producer_name}' registered with ID {producer_id} and Port {socket_port}.")
    return producer_id, socket_port, IP

def generate_items_for_producer(producer_id, num_items):
    products = load_data(products_file)
    producers = load_data(producers_file)
    all_products = [dict(prod, Category=category) for category, prod_list in products.items() for prod in prod_list]
    selected = random.sample(all_products, min(num_items, len(all_products)))
    producer = next((p for p in producers if p['ID'] == producer_id), None)
    with Lock:
        for prod in selected:
            price = random.uniform(prod['Price'][0], prod['Price'][1])
            quantity = random.randint(prod['Quantity'][0], prod['Quantity'][1])
            generated = {"Name": prod['ProductName'], "Category": prod['Category'], "Price": round(price, 2), "Quantity": quantity}
            producer['Products'].append(generated)
        save_data(producers_file, producers)
    print(f"{num_items} items generated.")

def format_products(products):
    return [f"{p['Name']} - Category: {p.get('Category', 'Unknown')} - Price: {p['Price']:.2f} - Quantity: {p['Quantity']}" for p in products]

def replenish_stock_periodically(producer_id):
    interval_seconds = 30
    while True:
        time.sleep(interval_seconds)
        producers = load_data(producers_file)
        producer = next((p for p in producers if p["ID"] == producer_id), None)
        if producer and producer['Products']:
            to_update_count = random.randint(1, len(producer['Products']))
            to_update = random.sample(producer['Products'], to_update_count)
            with Lock:
                for prod in to_update:
                    current_stock = prod.get('Quantity', 0)
                    max_qty = random.randint(100, 200)
                    new_stock = min(current_stock + random.randint(5, 20), max_qty)
                    prod['Quantity'] = new_stock
                    print(f"Stock for '{prod['Name']}' updated to {new_stock} [Old: {current_stock}].")
            save_data(producers_file, producers)

def list_products_endpoint(client_sock, producer_id):
    producers = load_data(producers_file)
    producer = next((p for p in producers if p['ID'] == producer_id), None)
    products = producer['Products'] if producer else []
    response = "\n".join(format_products(products)) if products else "No products available."
    client_sock.sendall(response.encode())

def purchase_product_endpoint(client_sock, producer_id, product_name, quantity):
    producers = load_data(producers_file)
    producer = next((p for p in producers if p['ID'] == producer_id), None)
    with Lock:
        info = next((prod for prod in producer['Products'] if prod['Name'] == product_name), None)
        if info and info['Quantity'] >= quantity:
            info['Quantity'] -= quantity
            save_data(producers_file, producers)
            response = f"Purchase successful! You bought {quantity} of {product_name}."
            print(f"Client bought {quantity} of '{product_name}'.")
        else:
            response = "Product not found or insufficient quantity."
            print(f"Purchase failed: Product '{product_name}' not found or insufficient quantity.")
    client_sock.sendall(response.encode())

def handle_connection(client_sock, addr, connections, marketplace_products, producer_id):
    try:
        print(f"Connection established with {addr}.")
        with client_sock:
            while True:
                data = client_sock.recv(1024).decode()
                if not data:
                    break
                if data.startswith("SUBSCRIBE_PRODUCT"):
                    _, product_name, quantity = data.split(',', maxsplit=2)
                    quantity = int(quantity)
                    marketplace_products.setdefault(addr, []).append((product_name, quantity))
                    purchase_product_endpoint(client_sock, producer_id, product_name, quantity)
                elif data.startswith("LIST_PRODUCTS"):
                    list_products_endpoint(client_sock, producer_id)
                elif data.startswith("HEARTBEAT"):
                    client_sock.sendall("OK".encode('utf-8'))
    except Exception as e:
        print(f"Connection error with {addr}: {e}")
    finally:
        print(f"Connection closed with {addr}.")

def producer_server(producer_name, producer_id, port, ip):
    global server_active
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind(('', port))
    server_sock.listen(5)
    print(f"Producer server '{producer_name}' started on IP {ip} and port {port}.")
    connections = []
    marketplace_products = {}
    threading.Thread(target=replenish_stock_periodically, args=(producer_id,)).start()
    while server_active:
        try:
            server_sock.settimeout(1.0)
            try:
                client_sock, addr = server_sock.accept()
            except socket.timeout:
                continue
            threading.Thread(target=handle_connection, args=(client_sock, addr, connections, marketplace_products, producer_id)).start()
        except OSError:
            break
    server_sock.close()
    print(f"Producer server '{producer_name}' stopped.")

def login_producer():
    producer_name = input("Enter producer name: ")
    producer_id = input("Enter producer ID: ")
    producers = load_data(producers_file)
    producer = next((p for p in producers if p['Name'] == producer_name and str(p['ID']) == producer_id), None)
    if producer:
        print(f"Welcome back, {producer['Name']}!")
        return producer['Name'], producer['ID'], producer['Port'], producer['IP']
    else:
        print("Producer not found.")
        return None, None, None

def main_menu():
    while True:
        choice = input("\n--- Main Menu ---\n1. Create new producer\n2. Log in as existing producer\n99. Exit\nChoose an option: ")
        if choice == '1':
            producer_name = input("Enter new producer name: ")
            producer_id, port, ip = register_producer(producer_name)
            generate_items_for_producer(producer_id, random.randint(3, 5))
            producer_server(producer_name, producer_id, port, ip)
            break
        elif choice == '2':
            producer_name, producer_id, port, ip = login_producer()
            if producer_name and producer_id:
                producer_server(producer_name, producer_id, port, ip)
            break
        elif choice == '99':
            print("Exiting...")
            break

if __name__ == "__main__":
    main_menu()
