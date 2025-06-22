from app.models.base_model import BaseModel
# If you are using SQLAlchemy, you would typically import these for ORM mapping:
# from sqlalchemy import Column, String, Integer, ForeignKey
# from sqlalchemy.orm import relationship, Mapped, mapped_column # Mapped and mapped_column for modern SQLAlchemy 2.0+

# Assuming Place and User are also defined as SQLAlchemy models
# from app.models.place import Place
# from app.models.user import User

class Review(BaseModel):
    # If BaseModel does not include table mapping, you would add it here:
    # __tablename__ = 'reviews'

    # Attributes specific to Review, mapped to database columns.
    # These would be defined using SQLAlchemy's Column if not in BaseModel.
    # For example:
    # text: Mapped[str] = mapped_column(String(1024), nullable=False)
    # rating: Mapped[int] = mapped_column(Integer, nullable=False)

    # Foreign keys for relationships with Place and User.
    # These would typically be defined as:
    # place_id: Mapped[str] = mapped_column(ForeignKey('places.id'), nullable=False)
    # user_id: Mapped[str] = mapped_column(ForeignKey('users.id'), nullable=False)

    # ORM relationship definitions (allows access to review.place and review.user objects).
    # These link the foreign keys to the actual model objects.
    # For example:
    # place: Mapped["Place"] = relationship("Place", back_populates="reviews")
    # user: Mapped["User"] = relationship("User", back_populates="reviews")


    def __init__(self, text: str, rating: int, place_id: str, user_id: str, **kwargs):
        """
        Initializes a new Review instance.

        Args:
            text (str): The textual content of the review.
            rating (int): The rating given (between 1 and 5).
            place_id (str): The unique ID of the place associated with this review.
            user_id (str): The unique ID of the user who left this review.
            **kwargs: Additional arguments passed to BaseModel (e.g., for loading from DB).
        """
        # Input validation is performed here to ensure data integrity
        # before the base object is created or attributes are assigned.
        
        # Validate 'text' (required, non-empty string)
        if not text or not isinstance(text, str) or not text.strip():
            raise ValueError("Review text is required and must be a non-empty string.")
        
        # Validate 'rating' (required, integer between 1 and 5)
        if rating is None or not isinstance(rating, int) or rating < 1 or rating > 5:
            raise ValueError("Rating is required and must be an integer between 1 and 5.")
        
        # Validate 'place_id' (required, non-empty string)
        # Actual existence check would typically be done in a service/repository layer
        # before creating the Review object, or through database integrity constraints.
        if not place_id or not isinstance(place_id, str) or not place_id.strip():
            raise ValueError("Place ID is required and must be a non-empty string.")
        
        # Validate 'user_id' (required, non-empty string)
        if not user_id or not isinstance(user_id, str) or not user_id.strip():
            raise ValueError("User ID is required and must be a non-empty string.")

        # Call the parent class (BaseModel) constructor to handle common attributes (id, created_at, updated_at).
        super().__init__(**kwargs)
        
        # Assign persistent attributes
        self.text = text.strip()
        self.rating = rating
        self.place_id = place_id
        self.user_id = user_id

    def to_dict(self) -> dict:
        """
        Converts the Review object to a dictionary.
        Includes extended details of linked Place and User objects if they have been loaded by the ORM.
        This fulfills the requirement for data serialization to return extended attributes for related objects.
        """
        data = super().to_dict() # Start with attributes from BaseModel
        
        data.update({
            'text': self.text,
            'rating': self.rating,
            'place_id': self.place_id, # Always include the foreign key ID
            'user_id': self.user_id,   # Always include the foreign key ID
        })

        # Conditionally include full details of 'place' and 'user' if ORM relationships
        # have loaded these objects. This is crucial for returning extended attributes.
        # `hasattr(self, 'place')` checks if the relationship attribute exists and has been loaded.
        if hasattr(self, 'place') and self.place:
            data['place'] = self.place.to_dict()
        # else: If the related object is not loaded, you might choose to omit the key
        #      or set it to None, depending on API design. Here, we simply don't add it.

        if hasattr(self, 'user') and self.user:
            data['user'] = self.user.to_dict()
        # else: Similar logic for 'user' as for 'place'.

        return data

    def update(self, data: dict) -> bool:
        """
        Updates the attributes of the review with validation.
        Typically, only 'text' and 'rating' are modifiable for an existing review.

        Args:
            data (dict): A dictionary containing attributes to update.

        Returns:
            bool: True if any attributes were updated, False otherwise.
        """
        updated = False
        
        # Validate and update 'text' if present in the data
        if 'text' in data:
            new_text = data['text']
            if not isinstance(new_text, str) or not new_text.strip():
                raise ValueError("Text update is required and must be a non-empty string.")
            self.text = new_text.strip()
            updated = True
        
        # Validate and update 'rating' if present in the data
        if 'rating' in data:
            new_rating = data['rating']
            if not isinstance(new_rating, int) or new_rating < 1 or new_rating > 5:
                raise ValueError("Rating update is required and must be an integer between 1 and 5.")
            self.rating = new_rating
            updated = True
        
        # Note: 'place_id' and 'user_id' typically should NOT be modifiable for an existing review.
        # If an attempt is made, it can be ignored or an error can be raised.
        if 'place_id' in data or 'user_id' in data:
            # Option 1: Silently ignore (if considered immutable for direct update)
            print("Warning: Attempted to update read-only 'place_id' or 'user_id' in Review. Ignored.")
            # Option 2: Raise an error if modification is strictly forbidden
            # raise ValueError("Place ID and User ID cannot be updated directly for a review.")

        # Update the 'updated_at' timestamp via BaseModel.save() if any attribute was changed.
        if updated:
            self.save() # Ensure BaseModel.save() updates 'updated_at'
        return updated
