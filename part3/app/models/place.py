from app.models.base_model import BaseModel

class Place(BaseModel):
    def __init__(self, title, description, price, latitude, longitude, owner, amenities=None, reviews=None):
        super().__init__()

# Validation title (required, max 100 chars)
        if not title or len(title) > 100:
            raise ValueError("Title is required and must be 100 characters or less")

# Validation price (must be positive)
        if price is None or price < 0:
            raise ValueError("Price must be a positive value")

# Validation latitude (-90 to 90)
        if latitude is None or latitude < -90.0 or latitude > 90.0:
            raise ValueError("Latitude must be between -90.0 and 90.0")

# Validation longitude (-180 to 180)
        if longitude is None or longitude < -180.0 or longitude > 180.0:
            raise ValueError("Longitude must be between -180.0 and 180.0")

# Validation owner (required)
        if not owner:
            raise ValueError("Owner is required")

        self.title = title
        self.description = description
        self.price = price
        self.latitude = latitude
        self.longitude = longitude
        self.owner = owner
        self.amenities = []
        self.reviews = []  # Liste pour stocker les reviews


    def add_review(self, review):
        """Add a review to the place."""
        self.reviews.append(review)


    def add_amenity(self, amenity):
        """Add an amenity to the place."""
        self.amenities.append(amenity)


    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'owner': self.owner.to_dict() if self.owner else None,
            'amenities': [amenity.to_dict() for amenity in self.amenities],
            'reviews': [review.to_dict() for review in self.reviews],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


    def update(self, data):
        """Update place attributes with validation"""
        for key, value in data.items():
            if key == 'title' and (not value or len(value) > 100):
                raise ValueError("Title must be 100 characters or less")
            elif key == 'price' and (value is None or value < 0):
                raise ValueError("Price must be positive")
            elif key == 'latitude' and (value < -90.0 or value > 90.0):
                raise ValueError("Latitude must be between -90.0 and 90.0")
            elif key == 'longitude' and (value < -180.0 or value > 180.0):
                raise ValueError("Longitude must be between -180.0 and 180.0")
            elif hasattr(self, key) and key != 'id':
                setattr(self, key, value)
        self.save()
