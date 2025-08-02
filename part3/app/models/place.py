from app import db
from app.models.base_model import BaseModel
from sqlalchemy.orm import relationship 
from app.models.place_amenities import place_amenities # Assurez-vous que ce chemin est correct

class Place(BaseModel):
    # Name of the table in the DB
    __tablename__ = 'places'

    # Attributs related to the db's column
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(1024), nullable=True)
    
    # CORRECTION : Renommé 'price' en 'price_by_night' pour correspondre au schéma SQL
    price_by_night = db.Column(db.Float, nullable=False) 
    
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)

    # AJOUT DES NOUVELLES COLONNES ICI pour correspondre au schéma SQL
    number_rooms = db.Column(db.Integer, default=0, nullable=False)
    number_bathrooms = db.Column(db.Integer, default=0, nullable=False)
    max_guests = db.Column(db.Integer, default=1, nullable=False)
    # FIN DE L'AJOUT

    owner_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)

    # Relations
    # Ajout d'une relation vers l'Owner (User)
    owner = db.relationship('User', backref='places_owned', lazy=True) # lazy=True ou lazy='joined' selon le besoin de chargement immédiat

    reviews = db.relationship('Review', backref='place', lazy=True, cascade='all, delete-orphan')
    # Assurez-vous que Amenity a un back_populates='places' pour que cette relation fonctionne
    amenities = db.relationship('Amenity', secondary=place_amenities, back_populates='places', lazy='joined') # Ajouté lazy='joined' pour faciliter le GET

    def __repr__(self):
        return f"<Place {self.title}>"

    def to_dict(self):
        # Utilise super().to_dict() pour hériter les champs de BaseModel (id, created_at, updated_at)
        data = super().to_dict() 
        data.update({
            'title': self.title,
            'description': self.description,
            'price_by_night': self.price_by_night, # Utilisez 'price_by_night'
            'latitude': self.latitude,
            'longitude': self.longitude,
            'number_rooms': self.number_rooms,       # Inclure
            'number_bathrooms': self.number_bathrooms, # Inclure
            'max_guests': self.max_guests,           # Inclure
            'owner_id': self.owner_id,               # Inclure l'ID du propriétaire
            
            # Pour les relations, Flask-RESTX attend des dictionnaires imbriqués pour place_output_model
            # Assurez-vous que .to_dict() existe pour Amenity et Review
            'owner': self.owner.to_dict() if self.owner else None, # Inclure l'objet owner complet si chargé
            'amenities': [amenity.to_dict() for amenity in self.amenities], # Inclure les objets amenities complets
            'reviews': [review.to_dict() for review in self.reviews] # Inclure les objets reviews complets
        })
        return data
