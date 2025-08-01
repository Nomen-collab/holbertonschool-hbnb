# Dans holbertonschool-hbnb/part3/run.py

from app import create_app
from app import db # Importez l'instance 'db' de SQLAlchemy depuis app/__init__.py
from flask_migrate import Migrate # Importez Flask-Migrate

app = create_app()

# Initialiser Flask-Migrate APRÈS la création de l'app et l'initialisation de db
# Cela lie l'extension Migrate à votre application Flask et à votre base de données SQLAlchemy
migrate = Migrate(app, db) # AJOUTEZ CETTE LIGNE

if __name__ == '__main__':
    app.run(debug=True)
