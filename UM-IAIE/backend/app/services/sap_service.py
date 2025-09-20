# Lógica para comunicação com SAP
import requests

class SAPService:
    BASE_URL = "https://sapserver/api"  # URL base do SAP
    TOKEN = "your_sap_api_token"

    @staticmethod
    def get_products():
        """Busca produtos no SAP."""
        url = f"{SAPService.BASE_URL}/products"
        headers = {"Authorization": f"Bearer {SAPService.TOKEN}"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()  # Lista de produtos
        else:
            raise Exception(f"Erro ao consultar o SAP: {response.text}")
