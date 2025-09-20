# Lógica para comunicação com Moloni
import requests

class MoloniService:
    BASE_URL = "https://api.moloni.pt/v1"
    TOKEN = "your_moloni_api_token"

    @staticmethod
    def create_product(product):
        """Cria um produto no Moloni."""
        url = f"{MoloniService.BASE_URL}/products/insert"
        headers = {"Authorization": f"Bearer {MoloniService.TOKEN}"}
        data = {
            "category_id": 1,  # ID da categoria no Moloni
            "name": product['name'],
            "price": product['price'],
            "stock": product['stock'],
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()  # Produto criado
        else:
            raise Exception(f"Erro ao criar produto no Moloni: {response.text}")
