# Inicialização da aplicação Flask
from flask import Flask
from flask_cors import CORS
from .routes.sap import bp_sap
from .routes.moloni import bp_moloni
from .routes.imgur import bp_imgur

def create_app():
    app = Flask(__name__)
    
    CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}}) 

    app.register_blueprint(bp_sap, url_prefix="/api/sap")
    app.register_blueprint(bp_moloni, url_prefix="/api/moloni")
    app.register_blueprint(bp_imgur, url_prefix="/api/imgur")
    
    return app