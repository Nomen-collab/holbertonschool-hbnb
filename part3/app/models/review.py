from sqlalchemy import Column, String, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base_model import BaseModel

class Review(BaseModel):
    """Review model with SQLAlchemy mapping"""
    
    __tablename__ = 'reviews'
    
    text = Column(Text, nullable=False)
    rating = Column(Integer, nullable=False)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    place_id = Column(String(36), ForeignKey('places.id'), nullable=False)
    
    # Relations
    user = relationship("User", back_populates="reviews")
    place = relationship("Place", back_populates="reviews")
    
    def __init__(self, text, rating, user_id, place_id):
        super().__init__()
        self.text = text
        self.rating = rating
        self.user_id = user_id
        self.place_id = place_id
    
    def to_dict(self):
        """Convert to dictionary"""
        data = super().to_dict()
        data.update({
            'text': self.text,
            'rating': self.rating,
            'user_id': self.user_id,
            'place_id': self.place_id
        })
        return data
    
    def __repr__(self):
        return f'<Review {self.id}>'
