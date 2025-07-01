"""
Initializing models and their relationships
"""
from app.models.base_model import BaseModel
from app.models.user import User
from app.models.place import Place
from app.models.review import Review
from app.models.amenity import Amenity

# This import ensures that all relationships are properly configured
__all__ = ['BaseModel', 'User', 'Place', 'Review', 'Amenity']
