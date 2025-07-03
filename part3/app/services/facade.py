from app.persistence.repository import SQLAlchemyRepository
from app.models.user import User
from app.models.place import Place
from app.models.review import Review
from app.models.amenity import Amenity


class HBnBFacade:
    """Facade pattern for managing business operations with SQLAlchemy"""
    
    def __init__(self):
        self.user_repo = SQLAlchemyRepository(User)
        self.place_repo = SQLAlchemyRepository(Place)
        self.review_repo = SQLAlchemyRepository(Review)
        self.amenity_repo = SQLAlchemyRepository(Amenity)
    
    # User operations
    def create_user(self, user_data):
        """Create a user"""
        # Check email uniqueness
        if self.user_repo.get_by_attribute('email', user_data['email']):
            raise ValueError("Email already exists")
        
        user = User(**user_data)
        return self.user_repo.add(user)
    
    def get_user(self, user_id):
        """Retrieve a user"""
        return self.user_repo.get(user_id)
    
    def get_user_by_email(self, email):
        """Retrieve a user by email"""
        return self.user_repo.get_by_attribute('email', email)
    
    # Place operations
    def create_place(self, place_data):
        """Create a place"""
        # Check that the owner exists
        if not self.user_repo.get(place_data['owner_id']):
            raise ValueError("Owner not found")
        
        place = Place(**place_data)
        return self.place_repo.add(place)
    
    def get_place(self, place_id):
        """Recover a place"""
        return self.place_repo.get(place_id)
    
    def get_all_places(self):
        """Recovers all locations"""
        return self.place_repo.get_all()
    
    # Review operations
    def create_review(self, review_data):
        """Create a review"""
        # Check that the user and location exist
        if not self.user_repo.get(review_data['user_id']):
            raise ValueError("User not found")
        if not self.place_repo.get(review_data['place_id']):
            raise ValueError("Place not found")
        
        review = Review(**review_data)
        return self.review_repo.add(review)
    
    def get_reviews_by_place(self, place_id):
        """Recover reviews of a place"""
        place = self.place_repo.get(place_id)
        return place.reviews if place else []
    
    # Amenity operations
    def create_amenity(self, amenity_data):
        """Create an amenity"""
        # Vérifier unicité du nom
        if self.amenity_repo.get_by_attribute('name', amenity_data['name']):
            raise ValueError("Amenity already exists")
        
        amenity = Amenity(**amenity_data)
        return self.amenity_repo.add(amenity)
    
    def get_amenity(self, amenity_id):
        """Recover an amenity"""
        return self.amenity_repo.get(amenity_id)
    
    def get_all_amenities(self):
        """Recover all amenities"""
        return self.amenity_repo.get_all()
