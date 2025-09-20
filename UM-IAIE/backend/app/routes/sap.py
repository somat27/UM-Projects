from flask import Blueprint, jsonify, request
from requests.auth import HTTPBasicAuth
import requests
from app.config import SAP_API_URL, SAP_CLIENT, SAP_AUTH_USER, SAP_AUTH_PASS
import traceback
import xmltodict

bp_sap = Blueprint('sap', __name__)

def get_token_sap():
    try:
        response = requests.get(
            SAP_API_URL,
            params={
                "$format": "json",
                "$filter": f"CreatedByUser eq '{SAP_AUTH_USER}'"
            },
            headers={
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "sap-client": SAP_CLIENT,
                "sap-ui-xx-viewCache": "false",
                "X-CSRF-Token": "fetch"
            },
            auth=HTTPBasicAuth(SAP_AUTH_USER, SAP_AUTH_PASS)
        )
        return response.headers.get("x-csrf-token"), response.cookies
    except:
        return

@bp_sap.route('/products', methods=['GET'])
def get_sap_products():
    try:
        response = requests.get(
            SAP_API_URL,
            params={
                "$format": "json",
                "$filter": f"CreatedByUser eq '{SAP_AUTH_USER}'"
            },
            headers={
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "sap-client": SAP_CLIENT,
                "sap-ui-xx-viewCache": "false"
            },
            auth=HTTPBasicAuth(SAP_AUTH_USER, SAP_AUTH_PASS)
        )
        if response.status_code == 200:
            return jsonify(response.json()["d"]["results"]), 200
        else:
            return jsonify({"error": "Erro ao buscar produtos do SAP", "details": response.text}), response.status_code
    except Exception as e:
        print("Erro ao inserir produto:", traceback.format_exc())
        return jsonify({"error": "Erro de comunicação com a API SAP", "details": str(e)}), 500

@bp_sap.route('/products', methods=['POST'])
def create_sap_product():
    try:
        token, cookies = get_token_sap()
        product_data = request.json
        product_data = {
            "ProductDescription": product_data["name"],
            "SizeOrDimensionText": product_data["category"],
            "ProductHierarchy": str(product_data["price"]),
            "ProductType": "FERT",
            "ProductType_Text": "Finished Product",
            "BaseUnit": "EA",
            "BaseUnit_Text": "Each",
        }
        response = requests.post(
            SAP_API_URL,
            headers={
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "sap-client": SAP_CLIENT,
                "X-CSRF-Token": token,
                "Content-Type": "application/json"
            },
            auth=HTTPBasicAuth(SAP_AUTH_USER, SAP_AUTH_PASS),
            cookies=cookies,
            json=product_data
        )
        print(response.text)
        if response.status_code in [200, 201]:
            try:
                response_data = xmltodict.parse(response.text)
                return jsonify({"message": "Produto criado com sucesso no SAP", "sap_response": response_data}), 201
            except Exception as e:
                return jsonify({"message": "Produto criado, mas falha ao processar resposta do SAP", "details": response.text}), 201
        else:
            return jsonify({"error": "Erro ao criar produto no SAP", "details": response.text}), response.status_code
    except Exception as e:
        return jsonify({"error": "Erro ao processar solicitação ao SAP", "details": str(e)}), 500