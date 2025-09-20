# ------------ Imports ------------ #
import json
import socket
import threading
import time
import psutil
import requests
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.x509 import load_pem_x509_certificate
from cryptography.exceptions import InvalidSignature
# ------------ Imports ------------ #

# ------------ Global Config ------------ #
COLOR_SUCCESS = '\033[92m'
COLOR_ERROR = '\033[91m'
COLOR_RESET = '\033[0m'
COLOR_DEBUG = '\033[94m'

PRODUCERS_FILE = 'Data/Producers.json'
purchased_subscriptions = {}
connections = {}
Lock = threading.RLock()
resale_fees = {}
DEFAULT_RESALE_FEE = 10.0
DEBUG = False

MANAGER_IP = "193.136.11.170"
MANAGER_PORT = 5001
# ------------ Global Config ------------ #

def debug(msg):
    if DEBUG:
        print(f"{COLOR_DEBUG}DEBUG: {COLOR_RESET}{msg}")

def show_error(msg):
    print(f"{COLOR_ERROR}Error: {COLOR_RESET}{msg}")

def show_success(msg):
    print(f"{COLOR_SUCCESS}Success: {COLOR_RESET}{msg}")

# ------------ REST helpers ------------ #
def get_producers_rest():
    url = f"http://{MANAGER_IP}:{MANAGER_PORT}/produtor"
    try:
        response = requests.get(url, timeout=3)
        producers = response.json() or []
        # Label connection type (manager returns 'secure' 1/0)
        for p in producers:
            p['Connection'] = "Secure REST" if p.get('secure') == 1 else "Insecure REST"
        return producers
    except requests.exceptions.RequestException as e:
        debug(f"Failed to fetch REST producers: {e}")
        return []

def load_manager_public_key_from_file():
    with open("manager_public_key.pem", 'rb') as f:
        pem = f.read()
    return load_pem_public_key(pem)

def verify_producer_cert_chain(prod_cert_pem: str):
    cert_obj = load_pem_x509_certificate(prod_cert_pem.encode('utf-8'))
    mgr_pub = load_manager_public_key_from_file()
    try:
        mgr_pub.verify(
            cert_obj.signature,
            cert_obj.tbs_certificate_bytes,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        debug("Producer certificate verified against manager public key.")
    except Exception as e:
        debug(f"Certificate verification failed: {e}")
        raise

def load_producer_cert(cert_pem: str):
    return load_pem_x509_certificate(cert_pem.encode('utf-8'))

def verify_signed_payload(cert_pem: str, signature_text: str, message):
    cert = load_producer_cert(cert_pem)
    pub = cert.public_key()

    # signature arrives as cp437 string (kept for compatibility)
    signature = signature_text.encode('cp437')

    if isinstance(message, (list, dict)):
        message = json.dumps(message).encode('utf-8')
    elif isinstance(message, str):
        message = message.encode('utf-8')

    try:
        pub.verify(
            signature,
            message,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )
        return True
    except InvalidSignature:
        return False
    except Exception as e:
        debug(f"Signature verification error: {e}")
        return False

def get_secure_categories_rest(ip, port):
    url = f"http://{ip}:{port}/secure/categories"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200:
            debug(f"Secure /categories error {r.status_code}")
            return []
        data = r.json()
        if not all(k in data for k in ("message", "signature", "certificate")):
            debug(f"Unexpected payload: {data}")
            return []
        verify_producer_cert_chain(data["certificate"])
        if verify_signed_payload(data["certificate"], data["signature"], data["message"]):
            return data["message"]
        debug("Invalid signature on /secure/categories")
        return []
    except requests.exceptions.RequestException as e:
        debug(f"Secure categories error: {e}")
        return []

def get_insecure_categories_rest(ip, port):
    url = f"http://{ip}:{port}/categories"
    try:
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else []
    except requests.exceptions.RequestException as e:
        debug(f"Insecure categories error: {e}")
        return []

def get_categories_rest():
    results = []
    rest_producers = get_producers_rest()
    for p in rest_producers:
        ip = p.get('ip')
        port = p.get('porta') or p.get('port')  # tolerate both keys
        name = p.get('nome') or p.get('name')
        conn = p.get('Connection', 'REST')

        if not (ip and port):
            debug(f"Invalid producer record from manager: {p}")
            continue

        if conn == "Secure REST":
            cats = get_secure_categories_rest(ip, port)
        else:
            cats = get_insecure_categories_rest(ip, port)

        if cats:
            results.append({
                "Name": name,
                "IP": ip,
                "PORT": int(port),
                "Connection": conn,
                "Categories": cats
            })
    return results

def get_insecure_products_by_category(ip, port, category):
    url = f"http://{ip}:{port}/products?category={category}"
    try:
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else []
    except requests.exceptions.RequestException as e:
        debug(f"Insecure products error: {e}")
        return []

def get_secure_products_by_category(ip, port, category):
    url = f"http://{ip}:{port}/secure/products?category={category}"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200:
            return []
        data = r.json()
        if not all(k in data for k in ("message", "signature", "certificate")):
            debug(f"Unexpected payload: {data}")
            return []
        verify_producer_cert_chain(data["certificate"])
        if verify_signed_payload(data["certificate"], data["signature"], data["message"]):
            return data["message"]
        debug("Invalid signature on /secure/products")
        return []
    except requests.exceptions.RequestException as e:
        debug(f"Secure products error: {e}")
        return []

def buy_insecure(ip, port, product, quantity):
    url = f"http://{ip}:{port}/buy/{product}/{quantity}"
    try:
        r = requests.get(url, timeout=5)
        return r.status_code == 200
    except requests.exceptions.RequestException:
        return False

def buy_secure(ip, port, product, quantity):
    url = f"http://{ip}:{port}/secure/buy/{product}/{quantity}"
    try:
        r = requests.post(url, timeout=5)
        if r.status_code != 200:
            return False
        data = r.json()
        if not all(k in data for k in ("message", "signature", "certificate")):
            return False
        verify_producer_cert_chain(data["certificate"])
        return verify_signed_payload(data["certificate"], data["signature"], data["message"])
    except requests.exceptions.RequestException:
        return False
# ------------ REST helpers ------------ #

# ------------ Socket helpers ------------ #
def get_socket_producers():
    active = []
    with open(PRODUCERS_FILE, 'r', encoding='utf-8') as f:
        file_producers = json.load(f)
    for sp in file_producers:
        ip = sp['IP']
        port = int(sp['Port'])
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2)
                if s.connect_ex((ip, port)) == 0:
                    active.append(sp)
        except Exception as e:
            debug(f"Socket test error {ip}:{port} -> {e}")
    return active

def get_socket_categories():
    out = []
    for sp in get_socket_producers():
        ip = sp['IP']; port = int(sp['Port'])
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2)
                s.connect((ip, port))
                s.sendall("LIST_CATEGORIES".encode('utf-8'))
                data = s.recv(1024).decode('utf-8')
                categories = [c for c in data.split("\n")[1:] if c]
                if categories:
                    out.append({
                        "Name": sp['Name'],
                        "IP": ip,
                        "PORT": port,
                        "Connection": "Socket",
                        "Categories": categories
                    })
        except Exception as e:
            debug(f"get_socket_categories error {ip}:{port} -> {e}")
    return out

def connect_producer(ip, port, producer_name):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, int(port)))
        return s
    except socket.error as e:
        debug(f"Connect failed {producer_name} {ip}:{port} -> {e}")
        return None

def heartbeat_thread(sock, ip, port, producer_name, timeout=30):
    fails = 0
    while fails * 2 < timeout:
        with Lock:
            try:
                sock.sendall(b"HEARTBEAT")
                resp = sock.recv(1024).decode('utf-8')
                if resp != "OK":
                    raise socket.error("Unexpected response")
                fails = 0
            except socket.error:
                fails += 1
                print(f"Lost connection to {producer_name} ({ip}:{port}) - attempt {fails}")
                new_sock = connect_producer(ip, port, producer_name)
                if new_sock:
                    print(f"Reconnected to {producer_name} ({ip}:{port})")
                    sock.close()
                    sock = new_sock
                    connections[(ip, port)] = (sock, producer_name)
        time.sleep(2)
    print(f"Producer {producer_name} ({ip}:{port}) disconnected > {timeout}s. Cleaning up.")
    remove_producer_products(producer_name, ip, port)

def remove_producer_products(producer_name, ip, port):
    with Lock:
        connections.pop((ip, port), None)
        purchased_subscriptions.pop(producer_name, None)
# ------------ Socket helpers ------------ #

# ------------ Common helpers ------------ #
def get_vpn_ip():
    for _, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET and addr.address.startswith('10.'):
                return addr.address
    return None

def get_products_by_category(producer, chosen_category):
    # Socket
    if producer['Connection'] == "Socket":
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(10)
                s.connect((producer['IP'], int(producer['PORT'])))
                s.sendall(f"LIST_PRODUCTS_CATEGORY,{chosen_category}".encode('utf-8'))
                resp = s.recv(4096).decode('utf-8')
                return json.loads(resp)
        except Exception as e:
            debug(f"Socket products error: {e}")
            return []
    # REST
    if producer['Connection'] == "Secure REST":
        return get_secure_products_by_category(producer['IP'], producer['PORT'], chosen_category)
    if producer['Connection'] == "Insecure REST":
        return get_insecure_products_by_category(producer['IP'], producer['PORT'], chosen_category)
    return []

def list_products(products_for_category):
    print("\nProducts available:")
    pid = 1
    for pinfo in products_for_category:
        print(f"Producer: {pinfo['Name']} ({pinfo['IP']}:{pinfo['PORT']}) - {pinfo['Connection']}")
        for prod in pinfo['Products']:
            print(f"{pid}. Product: {prod['product']} - Price: {prod['price']} - Available: {prod['quantity']}")
            prod['id'] = pid
            pid += 1

def buy_product_socket(producer_info, product_name, qty):
    ip = producer_info['IP']; port = producer_info['PORT']; name = producer_info['Name']
    sock = connect_producer(ip, port, name)
    if not sock:
        print(f"Could not connect to producer {name} ({ip}:{port}).")
        return False
    try:
        with sock:
            sock.settimeout(30)
            sock.sendall(f"SUBSCRIBE_PRODUCT,{product_name},{qty}".encode('utf-8'))
            reply = sock.recv(1024).decode('utf-8')
            if reply == "OK":
                print(f"Purchase OK: {qty} x {product_name}")
                with Lock:
                    purchased_subscriptions.setdefault(name, {"ip": ip, "port": port, "connection": "Socket", "products": []})
                    purchased_subscriptions[name]["products"].append({"name": product_name, "quantity": qty})
                    connections[(ip, port)] = (sock, name)
                threading.Thread(target=heartbeat_thread, args=(sock, ip, port, name), daemon=True).start()
                return True
            else:
                debug(f"Socket purchase failed: {reply}")
                return False
    except Exception as e:
        debug(f"Socket purchase error: {e}")
        return False

def buy_products(products_for_category, chosen_ids):
    # Flatten
    flat = []
    for pinfo in products_for_category:
        for prod in pinfo['Products']:
            flat.append((pinfo, prod))

    for pid in chosen_ids:
        match = next(((pinfo, prod) for pinfo, prod in flat if prod.get('id') == pid), None)
        if not match:
            show_error(f"Product with ID {pid} not found.")
            continue

        pinfo, product = match
        if product['quantity'] == 0:
            show_error(f"Sorry, {product['product']} is out of stock.")
            continue

        try:
            desired = int(input(f"How many '{product['product']}'? "))
            if desired <= 0:
                show_error("Invalid quantity. Enter a positive number.")
                continue
            if desired > product['quantity']:
                show_error(f"Only {product['quantity']} available for {product['product']}.")
                continue

            ok = False
            if pinfo['Connection'] == 'Socket':
                ok = buy_product_socket(pinfo, product['product'], desired)
            elif pinfo['Connection'] == 'Secure REST':
                ok = buy_secure(pinfo['IP'], pinfo['PORT'], product['product'], desired)
            elif pinfo['Connection'] == 'Insecure REST':
                ok = buy_insecure(pinfo['IP'], pinfo['PORT'], product['product'], desired)

            if ok:
                product['quantity'] -= desired
                name = pinfo["Name"]; ip = pinfo["IP"]; port = pinfo["PORT"]; conn = pinfo["Connection"]
                purchased_subscriptions.setdefault(name, {"ip": ip, "port": port, "connection": conn, "products": []})
                existing = next((x for x in purchased_subscriptions[name]["products"] if x["name"] == product['product']), None)
                if existing:
                    existing["quantity"] += desired
                else:
                    # price not strictly needed; store if present
                    price = product.get("price")
                    purchased_subscriptions[name]["products"].append({"name": product['product'], "quantity": desired, "price": price})
                show_success(f"Purchased {desired} x {product['product']}.")
            else:
                show_error(f"Failed to purchase {desired} x {product['product']}.")
        except ValueError:
            debug("Invalid number. Try again.")

def list_subscriptions():
    if not purchased_subscriptions:
        show_error("You have no subscriptions.")
        return
    print("--- Active Subscriptions ---")
    for producer_name, data in purchased_subscriptions.items():
        ip = data["ip"]; port = data["port"]; conn = data.get("connection", "")
        print(f"Producer: {producer_name} (IP: {ip}, Port: {port}, {conn})")
        for prod in data["products"]:
            name = prod["name"]; qty = int(prod["quantity"])
            buy_price = float(prod.get("price") or 0)
            fee_pct = float(resale_fees.get(name, DEFAULT_RESALE_FEE))
            fee_val = round(buy_price * fee_pct, 2)
            sell_price = buy_price + (fee_val / 100)
            print(f" - {name} - Quantity: {qty}")
            print(f"\tSale Price: {sell_price:.2f}€ ( Buy: {buy_price:.2f}€ | Resale Fee: {fee_pct}% )")

def set_resale_fee():
    try:
        print("\n--- Set Resale Fee ---")
        print("\nAvailable products:")
        flat = []
        idx = 1
        for data in purchased_subscriptions.values():
            for p in data["products"]:
                print(f"{idx}. Product: {p['name']} - Buy Price: {p.get('price','-')}")
                flat.append(p)
                idx += 1
        if not flat:
            print("No products in subscriptions.")
            return
        n = int(input("\nChoose a product number: "))
        if n < 1 or n > len(flat):
            show_error("Invalid product number.")
            return
        chosen = flat[n-1]
        fee = float(input("New resale fee (%): "))
        if fee < 0:
            show_error("Fee cannot be negative.")
            return
        resale_fees[chosen['name']] = fee
        show_success(f"Resale fee for '{chosen['name']}' set to {fee}%.")
    except ValueError:
        show_error("Invalid number.")

def marketplace_menu():
    while True:
        print("\n--- Marketplace Menu ---")
        print("1. List subscriptions")
        print("2. Buy products")
        print("3. Set resale fee")
        print("99. Exit")
        choice = input("Choose an option: ").strip()
        if choice == '1':
            list_subscriptions()
        elif choice == '2':
            main()
        elif choice == '3':
            set_resale_fee()
        elif choice == '99':
            show_success("Leaving the Marketplace. See you soon!")
            time.sleep(1)
            break
        else:
            show_error("Invalid option. Try again.")

def main():
    print("Loading categories...")
    producers_with_category = []
    products_for_category = []
    available_categories = set()

    rest = get_categories_rest()
    sock = get_socket_categories()
    all_producers = rest + sock

    if not all_producers:
        show_error("No categories available. Try again.")
        return

    for p in all_producers:
        print(f"{p['Name']} (IP: {p['IP']}:{p['PORT']}) - {p['Connection']}")
        for c in p.get('Categories', []):
            print(f" - {c}")
        available_categories.update(p.get('Categories', []))

    if not available_categories:
        show_error("No categories listed by producers. Try again.")
        return

    print("\nAvailable Categories:")
    print(", ".join(sorted(available_categories)))

    while True:
        chosen = input("\nChoose a category: ").strip()
        producers_with_category = [p for p in all_producers if chosen in p.get('Categories', [])]
        if producers_with_category:
            break
        show_error(f"Category '{chosen}' not available. Try again.")

    for p in producers_with_category:
        prods = get_products_by_category(p, chosen)
        if prods:
            products_for_category.append({
                "Name": p['Name'],
                "IP": p['IP'],
                "PORT": p['PORT'],
                "Connection": p['Connection'],
                "Products": prods
            })

    if not products_for_category:
        show_error(f"No products available in '{chosen}'.")
        return

    list_products(products_for_category)

    raw = input("\nEnter the numbers of the products to buy (comma-separated): ")
    try:
        ids = list(map(int, raw.split(','))) if raw.strip() else []
    except ValueError:
        show_error("Invalid input. Use comma-separated numbers.")
        return

    if ids:
        buy_products(products_for_category, ids)
    marketplace_menu()

if __name__ == "__main__":
    ip = get_vpn_ip()
    if ip:
        show_success(f"VPN IP detected: {ip}")
        main()
    else:
        show_error("VPN IP not detected — try again!")