from app.models.base_model import BaseModel

class Review(BaseModel):
    def __init__(self, text, rating, place, user):
        super().__init__()
        
        # Validation text (required)
        if not text or not text.strip():
            raise ValueError("Text is required")
        
        # Validation rating (1 to 5)
        if rating is None or rating < 1 or rating > 5:
            raise ValueError("Rating must be between 1 and 5")
        
        # Validation place (required)
        if not place:
            raise ValueError("Place is required")
        
        # Validation user (required)
        if not user:
            raise ValueError("User is required")
        
        self.text = text.strip()
        self.rating = int(rating)
        self.place = place
        self.user = user

    def to_dict(self):
        return {
            'id': self.id,
            'text': self.text,
            'rating': self.rating,
            'place': self.place.to_dict() if self.place else None,
            'user': self.user.to_dict() if self.user else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def update(self, data):
        """Update review attributes with validation"""
        for key, value in data.items():
            if key == 'text' and (not value or not value.strip()):
                raise ValueError("Text is required")
            elif key == 'rating' and (value < 1 or value > 5):
                raise ValueError("Rating must be between 1 and 5")
            elif hasattr(self, key) and key != 'id':
                setattr(self, key, value)
        self.save()
