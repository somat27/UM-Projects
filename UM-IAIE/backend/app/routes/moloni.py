from flask import Blueprint, jsonify, request
import requests
import time
from app.config import (
    MOLONI_API_URL,
    MOLONI_CLIENT_ID,
    MOLONI_CLIENT_SECRET,
    MOLONI_USERNAME,
    MOLONI_PASSWORD,
)
from urllib.parse import urlencode

bp_moloni = Blueprint('moloni', __name__)

# --------------- Acess Token --------------- #
moloni_tokens = {
    "access_token": None,
    "refresh_token": None,
    "expires_at": 0,  
}

def get_moloni_access_token():
    if moloni_tokens["access_token"] and time.time() < moloni_tokens["expires_at"]:
        return moloni_tokens["access_token"]
    if moloni_tokens["refresh_token"] and time.time() >= moloni_tokens["expires_at"]:
        return refresh_moloni_access_token()
    try:
        url = (
            f"{MOLONI_API_URL}/grant/?grant_type=password"
            f"&client_id={MOLONI_CLIENT_ID}"
            f"&client_secret={MOLONI_CLIENT_SECRET}"
            f"&username={MOLONI_USERNAME}"
            f"&password={MOLONI_PASSWORD}"
        )
        response = requests.post(url)
        if response.status_code == 200:
            data = response.json()
            moloni_tokens["access_token"] = data["access_token"]
            moloni_tokens["refresh_token"] = data["refresh_token"]
            moloni_tokens["expires_at"] = time.time() + data["expires_in"] 
            return moloni_tokens["access_token"]
        else:
            raise Exception(f"Erro ao obter access_token: {response.text}")
    except Exception as e:
        raise Exception(f"Erro ao obter access_token: {str(e)}")

def refresh_moloni_access_token():
    try:
        if not moloni_tokens["refresh_token"]:
            raise Exception("Refresh token ausente. Refaça a autenticação.")
        url = (
            f"{MOLONI_API_URL}/grant/?grant_type=refresh_token"
            f"&client_id={MOLONI_CLIENT_ID}"
            f"&client_secret={MOLONI_CLIENT_SECRET}"
            f"&refresh_token={moloni_tokens['refresh_token']}"
        )
        response = requests.post(url)
        if response.status_code == 200:
            data = response.json()
            moloni_tokens["access_token"] = data["access_token"]
            moloni_tokens["refresh_token"] = data["refresh_token"]
            moloni_tokens["expires_at"] = time.time() + data["expires_in"] 
            return moloni_tokens["access_token"]
        else:
            raise Exception(f"Erro ao atualizar access_token: {response.text}")
    except Exception as e:
        raise Exception(f"Erro ao atualizar access_token: {str(e)}")
# --------------- Acess Token --------------- #
    
# --------------- Routes --------------- #
@bp_moloni.route('/products', methods=['POST'])
def get_moloni_products():
    try:
        token = get_moloni_access_token()
        url = f"{MOLONI_API_URL}/products/getAll/?access_token={token}"
        response = requests.post(
            url,
            data={"company_id": 322336},
            headers={"Content-Type": "application/x-www-form-urlencoded"}  
        )
        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({"error": "Erro ao buscar produtos no Moloni", "details": response.text}), response.status_code
    except Exception as e:
        return jsonify({"error": "Erro de comunicação com o Moloni", "details": str(e)}), 500

def create_category(company_id, token, name, description="", parent_id=0):
    url = f"https://api.moloni.pt/v1/productCategories/insert/?access_token={token}"
    response = requests.post(
        url,
        data={
            "company_id": company_id,
            "name": name,
            "description": description,
            "parent_id": parent_id,
            "pos_enabled": 1 
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    if response.status_code in [200, 201]:
        return response.json()["category_id"]
    else:
        raise Exception(f"Erro ao criar categoria: {response.text}")

def get_categories_f(company_id, token):
    url = f"https://api.moloni.pt/v1/productCategories/getAll/?access_token={token}"
    response = requests.post(
        url,
        data={"company_id": company_id, "parent_id": 0},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    if response.status_code in [200, 201]:
        return response.json()
    else:
        raise Exception(f"Erro ao obter categorias: {response.text}")

def get_or_create_category(company_id, token, category_name):
    categories = get_categories_f(company_id, token)
    for category in categories:
        if category["name"] == category_name:
            return category["category_id"]
    return create_category(company_id, token, category_name)

@bp_moloni.route('/products/create', methods=['POST'])
def create_moloni_product():
    try:
        product_data = request.json
        token = get_moloni_access_token()
        company_id = 322336 
        category_name = product_data.get("category_name", "Categoria Padrão")
        category_id = get_or_create_category(company_id, token, category_name)
        product_data["category_id"] = category_id
        url = f"https://api.moloni.pt/v1/products/insert/?access_token={token}"
        response = requests.post(
            url,
            data=urlencode(product_data),
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        if response.status_code in [200, 201]:
            return jsonify({"message": "Produto criado com sucesso no Moloni", "moloni_response": response.json()}), 201
        else:
            return jsonify({"error": "Erro ao criar produto no Moloni", "details": response.text}), response.status_code
    except Exception as e:
        return jsonify({"error": "Erro ao processar solicitação ao Moloni", "details": str(e)}), 500

@bp_moloni.route('/invoices', methods=['POST'])
def get_invoices():
    try:
        token = get_moloni_access_token()
        url = f"{MOLONI_API_URL}/invoices/getAll/?access_token={token}"
        response = requests.post(
            url,
            data={"company_id": 322336},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({"error": "Erro ao buscar faturas no Moloni", "details": response.text}), response.status_code
    except Exception as e:
        return jsonify({"error": "Erro de comunicação com o Moloni", "details": str(e)}), 500

@bp_moloni.route('/customers', methods=['POST'])
def get_customers():
    try:
        token = get_moloni_access_token()
        url = f"{MOLONI_API_URL}/customers/getAll/?access_token={token}"
        response = requests.post(
            url,
            data={"company_id": 322336},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({"error": "Erro ao buscar clientes no Moloni", "details": response.text}), response.status_code
    except Exception as e:
        return jsonify({"error": "Erro de comunicação com o Moloni", "details": str(e)}), 500
    
@bp_moloni.route('/signup', methods=['POST'])
def signup():
    try:
        token = get_moloni_access_token()
        url_get_customers = f"{MOLONI_API_URL}/customers/getAll/?access_token={token}"
        url_insert_customer = f"{MOLONI_API_URL}/customers/insert/?access_token={token}"
        data = request.json
        if not data:
            return jsonify({"error": "Nenhum dado enviado."}), 400
        response = requests.post(url_get_customers, data={"company_id": 322336})
        if response.status_code != 200:
            return jsonify({"error": "Erro ao buscar clientes existentes.", "details": response.text}), response.status_code
        customers = response.json()
        if not customers:
            new_customer_number = 1
        else:
            highest_customer_number = max(int(customer.get("number", 0)) for customer in customers)
            new_customer_number = highest_customer_number + 1
        payload = {
            "company_id": 322336,
            "vat": data.get("vat"),
            "number": str(new_customer_number),
            "name": data.get("name"),
            "phone": data.get("phone"),
            "language_id": data.get("language_id", 1),
            "address": data.get("address"),
            "city": data.get("city"),
            "zip_code": data.get("zip_code"),
            "country_id": data.get("country_id", 1),
            "maturity_date_id": data.get("maturity_date_id", 2095441),
            "payment_method_id": data.get("payment_method_id", 2525311),
            "salesman_id": data.get("salesman_id", 0),
            "payment_day": data.get("payment_day", 0),
            "discount": data.get("discount", 0),
            "credit_limit": data.get("credit_limit", 0),
            "delivery_method_id": data.get("delivery_method_id", 1),
        }
        response = requests.post(
            url_insert_customer,
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        if response.status_code in [200, 201]:
            return jsonify({"message": "Conta criada com sucesso!", "details": response.json()}), 201
        else:
            return jsonify({"error": "Erro ao criar conta no Moloni", "details": response.text}), response.status_code
    except Exception as e:
        return jsonify({"error": "Erro de comunicação com o Moloni", "details": str(e)}), 500

@bp_moloni.route('/signin', methods=['POST'])
def signin():
    try:
        token = get_moloni_access_token()
        url_get_all = f"{MOLONI_API_URL}/customers/getAll/?access_token={token}"
        response = requests.post(
            url_get_all,
            data={"company_id": 322336},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        if response.status_code != 200:
            return jsonify({"error": "Erro ao buscar clientes", "details": response.text}), response.status_code
        all_customers = response.json()
        data = request.json
        if not data or "vat" not in data or "name" not in data:
            return jsonify({"error": "Nome e VAT são obrigatórios."}), 400
        customer = next(
            (c for c in all_customers if c["vat"] == data["vat"] and c["name"].lower() == data["name"].lower()), None
        )
        if not customer:
            return jsonify({"error": "Nome ou VAT incorretos."}), 404
        url_get_one = f"{MOLONI_API_URL}/customers/getOne/?access_token={token}"
        response_details = requests.post(
            url_get_one,
            data={"company_id": 322336, "customer_id": customer["customer_id"]},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        ) 
        if response_details.status_code == 200:
            return jsonify(response_details.json()), 200
        else:
            return jsonify({"error": "Erro ao buscar detalhes do cliente", "details": response_details.text}), response_details.status_code
    except Exception as e:
        return jsonify({"error": "Erro interno", "details": str(e)}), 500

@bp_moloni.route('/categories', methods=['POST'])
def get_categories():
    try:
        token = get_moloni_access_token()
        url = f"{MOLONI_API_URL}/productCategories/getAll/?access_token={token}"
        params = {
            "company_id": 322336,  
            "parent_id": 0         
        }
        response = requests.post(
            url,
            data=params,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        if response.status_code == 200:
            categories = response.json()
            return jsonify(categories), 200
        else:
            return jsonify({"error": "Erro ao buscar categorias", "details": response.text}), response.status_code
    except Exception as e:
        return jsonify({"error": "Erro ao processar a solicitação", "details": str(e)}), 500

@bp_moloni.route('/products/update', methods=['POST'])
def update_product():
    try:
        token = get_moloni_access_token()
        payload = request.json
        if not payload:
            return jsonify({"error": "Nenhum dado enviado."}), 400
        url = f"{MOLONI_API_URL}/products/update/?access_token={token}"
        response = requests.post(
            url,
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        print(response.text)
        if response.status_code == 200:
            return jsonify({"message": "Produto atualizado com sucesso.", "details": response.json()}), 200
        else:
            return jsonify({"error": "Erro ao atualizar produto.", "details": response.text}), response.status_code
    except Exception as e:
        return jsonify({"error": "Erro interno ao processar a atualização.", "details": str(e)}), 500
    
@bp_moloni.route('/products/delete', methods=['POST'])
def delete_product():
    try:
        token = get_moloni_access_token()
        payload = request.json
        if not payload or "company_id" not in payload or "product_id" not in payload:
            return jsonify({"error": "Campos obrigatórios estão faltando."}), 400
        url = f"{MOLONI_API_URL}/products/delete/?access_token={token}"
        response = requests.post(
            url,
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        if response.status_code == 200:
            return jsonify({"message": "Produto removido com sucesso.", "details": response.json()}), 200
        else:
            return jsonify({"error": "Erro ao remover produto.", "details": response.text}), response.status_code
    except Exception as e:
        return jsonify({"error": "Erro interno ao processar a remoção.", "details": str(e)}), 500
    
@bp_moloni.route('/categories/insert', methods=['POST'])
def insert_category():
    try:
        token = get_moloni_access_token()
        payload = request.json
        if not payload or "company_id" not in payload or "name" not in payload:
            return jsonify({"error": "Campos obrigatórios estão faltando."}), 400
        url = f"{MOLONI_API_URL}/productCategories/insert/?access_token={token}"
        response = requests.post(
            url,
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        if response.status_code == 200:
            return jsonify({"message": "Categoria criada com sucesso.", "details": response.json()}), 200
        else:
            return jsonify({"error": "Erro ao criar categoria.", "details": response.text}), response.status_code
    except Exception as e:
        return jsonify({"error": "Erro interno ao processar a criação.", "details": str(e)}), 500

@bp_moloni.route('/categories/delete', methods=['POST'])
def delete_category():
    try:
        token = get_moloni_access_token()
        data = request.json
        if not data.get("company_id") or not data.get("category_id"):
            return jsonify({"error": "Os campos company_id e category_id são obrigatórios."}), 400
        url = f"{MOLONI_API_URL}/productCategories/delete/?access_token={token}"
        response = requests.post(url, data={
            "company_id": data["company_id"],
            "category_id": data["category_id"]
        })
        if response.status_code == 200:
            return jsonify({"message": "Categoria removida com sucesso."}), 200
        else:
            return jsonify({"error": response.text}), response.status_code
    except Exception as e:
        return jsonify({"error": f"Erro ao remover a categoria: {str(e)}"}), 500
    
@bp_moloni.route('/customers/update', methods=['POST'])
def update_customer():
    try:
        token = get_moloni_access_token()
        customer_data = request.json
        required_fields = [
            'company_id', 'customer_id', 'vat', 'number', 'name',
            'language_id', 'address', 'city', 'country_id', 'maturity_date_id',
            'payment_method_id', 'document_type_id', 'copies'
        ]
        for field in required_fields:
            if field not in customer_data:
                return jsonify({"error": f"Campo obrigatório '{field}' está faltando."}), 400
        url = f"{MOLONI_API_URL}/customers/update/?access_token={token}"
        response = requests.post(url, data=customer_data, headers={"Content-Type": "application/x-www-form-urlencoded"})
        if response.status_code == 200:
            return jsonify({"success": True, "details": response.json()})
        else:
            return jsonify({"error": "Erro ao atualizar cliente no Moloni", "details": response.text}), response.status_code
    except Exception as e:
        return jsonify({"error": "Erro interno no servidor", "details": str(e)}), 500
    
@bp_moloni.route('/customers/delete', methods=['POST'])
def delete_customer():
    try:
        token = get_moloni_access_token()
        payload = request.json
        if 'customer_id' not in payload:
            return jsonify({"error": "O campo 'customer_id' é obrigatório."}), 400
        url = f"{MOLONI_API_URL}/customers/delete/?access_token={token}"
        response = requests.post(url, data={
            "company_id": payload['company_id'],
            "customer_id": payload['customer_id']
        })
        if response.status_code == 200:
            return jsonify({"message": "Cliente removido com sucesso!"}), 200
        else:
            return jsonify({
                "error": "Erro ao remover cliente.",
                "details": response.json()
            }), response.status_code
    except Exception as e:
        return jsonify({"error": "Erro ao comunicar com a API Moloni.", "details": str(e)}), 500

@bp_moloni.route('/paymentMethods', methods=['POST'])
def get_payment_methods():
    try:
        token = get_moloni_access_token()
        url = f"{MOLONI_API_URL}/paymentMethods/getAll/?access_token={token}"
        response = requests.post(
            url,
            data={"company_id": 322336},
            headers={"Content-Type": "application/x-www-form-urlencoded"}  
        )
        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({"error": "Erro ao buscar métodos de pagamento.", "details": response.text}), response.status_code
    except Exception as e:
        return jsonify({"error": "Erro ao processar solicitação ao Moloni", "details": str(e)}), 500

@bp_moloni.route('/internal_documents/insert', methods=['POST'])
def insert_internal_document():
    try:
        token = get_moloni_access_token()
        data = request.json
        url = f"{MOLONI_API_URL}/internalDocuments/insert/?access_token={token}&json=true"
        response = requests.post(
            url,
            json=data,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code in [200, 201]:
            return jsonify({"message": "Internal Document criado com sucesso.", "details": response.json()}), 201
        else:
            return jsonify({"error": "Erro ao criar Internal Document.", "details": response.text}), response.status_code
    except Exception as e:
        return jsonify({"error": "Erro ao processar solicitação ao Moloni", "details": str(e)}), 500
    
@bp_moloni.route('/documents/<int:customer_id>', methods=['POST'])
def get_customer_documents(customer_id):
    try:
        token = get_moloni_access_token()
        url = f"{MOLONI_API_URL}/documents/getAll/?access_token={token}"
        payload = {
            "company_id": 322336,  
            "customer_id": customer_id,
            "qty": 50, 
            "offset": 0
        }
        response = requests.post(url, data=payload, headers={"Content-Type": "application/x-www-form-urlencoded"})
        if response.status_code == 200:
            documents = response.json()
            return jsonify(documents), 200
        else:
            return jsonify({"error": "Erro ao buscar documentos.", "details": response.text}), response.status_code
    except Exception as e:
        return jsonify({"error": "Erro ao processar a solicitação.", "details": str(e)}), 500

@bp_moloni.route('/documents/details/<int:document_id>', methods=['POST'])
def get_document_details(document_id):
    try:
        token = get_moloni_access_token()
        url = f"{MOLONI_API_URL}/documents/getOne/?access_token={token}"
        payload = {
            "company_id": 322336,  
            "document_id": document_id
        }
        response = requests.post(url, data=payload, headers={"Content-Type": "application/x-www-form-urlencoded"})
        if response.status_code == 200:
            document_details = response.json()
            return jsonify(document_details.get("products", [])), 200
        else:
            return jsonify({"error": "Erro ao buscar detalhes do documento.", "details": response.text}), response.status_code
    except Exception as e:
        return jsonify({"error": "Erro ao processar a solicitação.", "details": str(e)}), 500
    
@bp_moloni.route('/internal-documents', methods=['POST'])
def get_internal_documents():
    try:
        token = get_moloni_access_token()
        url = f"{MOLONI_API_URL}/internalDocuments/getAll/?access_token={token}"
        payload = {
            "company_id": 322336,
            "qty": 50,  
            "offset": 0
        }
        response = requests.post(url, data=payload, headers={"Content-Type": "application/x-www-form-urlencoded"})
        if response.status_code == 200:
            internal_documents = response.json()
            return jsonify(internal_documents), 200
        else:
            return jsonify({"error": "Erro ao buscar documentos internos.", "details": response.text}), response.status_code
    except Exception as e:
        return jsonify({"error": "Erro ao processar a solicitação.", "details": str(e)}), 500
    
@bp_moloni.route('/product_stocks/insert', methods=['POST'])
def insert_product_stock():
    try:
        token = get_moloni_access_token()
        data = request.json
        url = f"{MOLONI_API_URL}/productStocks/insert/?access_token={token}"
        response = requests.post(url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
        if response.status_code == 200:
            return jsonify({"message": "Movimento de stock registrado com sucesso."}), 200
        else:
            return jsonify({"error": "Erro ao registrar movimento de stock.", "details": response.text}), response.status_code
    except Exception as e:
        return jsonify({"error": "Erro ao processar a solicitação.", "details": str(e)}), 500


#  --------------- Routes --------------- #