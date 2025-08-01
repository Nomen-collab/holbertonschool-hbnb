from app import db
from app.models.base_model import BaseModel
from sqlalchemy.orm import relationship # Ajoutez cet import
from app.models.place_amenities import place_amenities # <--- AJOUTEZ CETTE LIGNE

class Amenity(BaseModel):
    # name of the table in the DB
    __tablename__ = 'amenities'
    # name of the amenity
    name = db.Column(db.String(128), nullable=False, unique=True)

    places = db.relationship('Place', secondary=place_amenities, back_populates='amenities') # <--- Utilisez la variable directement ici

    def __repr__(self):
        return f"<Amenity {self.name}>"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
