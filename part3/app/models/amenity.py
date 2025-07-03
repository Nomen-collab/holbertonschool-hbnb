from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.models.base_model import BaseModel
from app.models.place import place_amenity

class Amenity(BaseModel):
    """Amenity model with SQLAlchemy mapping"""
    
    __tablename__ = 'amenities'
    
    name = Column(String(50), unique=True, nullable=False)
    
    # Relations
    places = relationship("Place", secondary=place_amenity, back_populates="amenities")
    
    def __init__(self, name):
        super().__init__()
        self.name = name
    
    def to_dict(self):
        """Convert to dictionary"""
        data = super().to_dict()
        data.update({
            'name': self.name
        })
        return data
    
    def __repr__(self):
        return f'<Amenity {self.name}>'

