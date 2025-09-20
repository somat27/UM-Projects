from flask import Blueprint, jsonify, request
import requests
from app.config import IMGUR_CLIENT_ID

bp_imgur = Blueprint('imgur', __name__)

@bp_imgur.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({"error": "Nenhum arquivo foi enviado"}), 400
    image_file = request.files['image']
    if image_file.filename == '':
        return jsonify({"error": "Nome de arquivo inválido"}), 400
    try:
        url = 'https://api.imgur.com/3/image'
        headers = {'Authorization': f'Client-ID {IMGUR_CLIENT_ID}'}
        files = {'image': image_file}
        response = requests.post(url, headers=headers, files=files)
        response_data = response.json()
        if response.status_code == 200 and response_data['success']:
            return jsonify({"link": response_data['data']['link']}), 200
        else:
            return jsonify({"error": response_data['data']['error']}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500