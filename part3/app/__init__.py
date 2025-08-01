from flask import Flask
from flask_restx import Api
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS # Importez CORS

# Initialisation des extensions Flask en dehors de la fonction create_app
# C'est important pour qu'elles soient des instances uniques et globales
bcrypt = Bcrypt()
jwt = JWTManager()
db = SQLAlchemy()

# Définition du schéma de sécurité pour Flask-RestX (pour le cadenas dans Swagger UI)
authorizations = {
    'Bearer Auth': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': "Collez votre jeton JWT ici. Format: 'Bearer <votre_jeton>'"
    }
}

def create_app(config_class="config.DevelopmentConfig"):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Configuration de CORS pour toutes les routes sous /api/
    # Ceci devrait résoudre les problèmes de requêtes OPTIONS 404
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Initialisation des extensions avec l'application Flask
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # Imports des Namespaces des APIs.
    # Ces imports doivent venir APRÈS l'initialisation de 'db' avec 'app'
    # pour éviter les RuntimeError liés à SQLAlchemy.
    from app.api.v1.users import api as users_ns
    from app.api.v1.amenities import api as amenities_ns
    from app.api.v1.places import api as places_ns
    from app.api.v1.reviews import api as reviews_ns
    from app.api.v1.auth import api as auth_ns

    # Création de l'instance Api pour Flask-RestX
    # Intégration des autorisations pour Swagger UI
    api = Api(
        app,
        version='1.0',
        title='HBnB API',
        description='HBnB Application API',
        security='Bearer Auth',  # Définit le schéma de sécurité par défaut pour toutes les routes documentées
        authorizations=authorizations # Fournit la définition du schéma de sécurité
    )

    # Ajout des Namespaces à l'API principale
    api.add_namespace(users_ns, path='/api/v1/users')
    api.add_namespace(amenities_ns, path='/api/v1/amenities')
    api.add_namespace(places_ns, path='/api/v1/places')
    api.add_namespace(reviews_ns, path='/api/v1/reviews')
    api.add_namespace(auth_ns, path='/api/v1/auth')

    return app
