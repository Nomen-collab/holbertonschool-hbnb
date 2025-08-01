from flask import Flask
from flask_restx import Api
from flask_jwt_extended import JWTManager # <--- AJOUTEZ CETTE LIGNE

from app.api.v1.users import api as users_ns
from app.api.v1.amenities import api as amenities_ns
from app.api.v1.places import api as places_ns
from app.api.v1.reviews import api as reviews_ns

def create_app():
    app = Flask(__name__)
    
    # <--- AJOUTEZ CES LIGNES POUR LA CONFIGURATION JWT
    # Configurez une clé secrète pour les tokens JWT
    app.config["JWT_SECRET_KEY"] = "votre_super_cle_secrete_ici"
    # Configurez l'emplacement du token (par exemple, dans les en-têtes)
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]
    # Initialisez Flask-JWT-Extended avec votre application
    jwt = JWTManager(app)
    # <--- FIN DES AJOUTS
    
    api = Api(app, version='1.0', title='HBnB API', description='HBnB Application API')

    # Register the users namespace
    api.add_namespace(users_ns, path='/api/v1/users')
    # Register the amenities namespace
    api.add_namespace(amenities_ns, path='/api/v1/amenities')
    # Register the places namespace
    api.add_namespace(places_ns, path='/api/v1/places')
    # Register the reviews namespace
    api.add_namespace(reviews_ns, path='/api/v1/reviews')
    
    return app
