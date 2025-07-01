from sqlalchemy import Column, String, Text, Integer, Float, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.models.base_model import BaseModel

# Association table for the Many-to-Many relationship between Place and Amenity
place_amenity = Table(
    'place_amenity',
    BaseModel.metadata,
    Column('place_id', String(36), ForeignKey('places.id'), primary_key=True),
    Column('amenity_id', String(36), ForeignKey('amenities.id'), primary_key=True)
)

class Place(BaseModel):
    """Place model with SQLAlchemy mapping"""
    
    __tablename__ = 'places'
    
    title = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    owner_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    
    # Relations
    owner = relationship("User", back_populates="places")
    reviews = relationship("Review", back_populates="place", cascade="all, delete-orphan")
    amenities = relationship("Amenity", secondary=place_amenity, back_populates="places")
    
    def __init__(self, title, description, price, latitude, longitude, owner_id):
        super().__init__()
        self.title = title
        self.description = description
        self.price = price
        self.latitude = latitude
        self.longitude = longitude
        self.owner_id = owner_id
    
    def to_dict(self):
        """Converts to a dictionary with relations"""
        data = super().to_dict()
        data.update({
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'owner_id': self.owner_id,
            'amenities': [amenity.to_dict() for amenity in self.amenities] if self.amenities else []
        })
        return data
    
    def __repr__(self):
        return f'<Place {self.title}>'
