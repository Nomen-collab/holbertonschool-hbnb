# app/models/place.py
from app.models.base_model import BaseModel
from datetime import datetime # Necessary import for timestamps


class Place(BaseModel):
    # Constructor with robust default values for optional fields
    # and lists of related objects.
    def __init__(self, title, description=None, price=None, latitude=None, longitude=None, owner=None, amenities=None, reviews=None):
        super().__init__()
        
        # Comprehensive type and constraint validations
        if not isinstance(title, str) or not title.strip():
            raise ValueError("Title is required and must be a non-empty string.")
        if len(title) > 100:
            raise ValueError("Title must be 100 characters or less.")

        if not isinstance(price, (int, float)) or price <= 0:
            raise ValueError("Price must be a positive number.")

        if not isinstance(latitude, (int, float)) or not (-90 <= latitude <= 90):
            raise ValueError("Latitude must be a number between -90 and 90.")

        if not isinstance(longitude, (int, float)) or not (-180 <= longitude <= 180):
            raise ValueError("Longitude must be a number between -180 and 180.")

        if owner is None: # owner must be a User object, not an ID
            raise ValueError("Owner object is required for a Place.")
        # Add stricter type checking for owner if desired
        # if not isinstance(owner, User):
        #    raise ValueError("Owner must be a User object.")

        self.title = title
        self.description = description if description is not None else "" # Ensures a default description
        self.price = price
        self.latitude = latitude
        self.longitude = longitude
        self.owner = owner # ✅ This is a User object
        
        # Initialization of lists for related objects
        self.amenities = amenities if amenities is not None else [] # ✅ List of Amenity objects
        self.reviews = reviews if reviews is not None else [] # ✅ List of Review objects

    def add_review(self, review):
        """Adds a review to the place. Ensures uniqueness."""
        if review not in self.reviews: # Checks for uniqueness
            self.reviews.append(review)

    def add_amenity(self, amenity):
        """Adds an amenity to the place. Ensures uniqueness."""
        if amenity not in self.amenities: # Checks for uniqueness
            self.amenities.append(amenity)

    def to_dict(self):
        # Converts related objects to dictionaries for JSON serialization
        owner_dict = self.owner.to_dict() if self.owner else None
        amenities_list = [amenity.to_dict() for amenity in self.amenities]
        reviews_list = [review.to_dict() for review in self.reviews]

        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'owner': owner_dict, # Owner object is converted to dict here
            'amenities': amenities_list, # Amenity objects are converted
            'reviews': reviews_list, # Review objects are converted
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def update(self, data):
        """Updates place attributes with validation."""
        updatable_fields = ['title', 'description', 'price', 'latitude', 'longitude']
        for key, value in data.items():
            if key in updatable_fields: # Checks if the field is updatable
                # Specific validations for fields
                if key == 'title':
                    if not isinstance(value, str) or not value.strip() or len(value) > 100:
                        raise ValueError("Title must be a non-empty string up to 100 characters.")
                elif key == 'price':
                    if not isinstance(value, (int, float)) or value <= 0:
                        raise ValueError("Price must be a positive number.")
                elif key == 'latitude':
                    if not isinstance(value, (int, float)) or not (-90 <= value <= 90):
                        raise ValueError("Latitude must be between -90.0 and 90.0.")
                elif key == 'longitude':
                    if not isinstance(value, (int, float)) or not (-180 <= value <= 180):
                        raise ValueError("Longitude must be between -180.0 and 180.0.")
                
                setattr(self, key, value) # Updates the attribute
        self.save() # Updates updated_at timestamp
