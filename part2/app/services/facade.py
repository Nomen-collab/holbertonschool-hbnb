from app.persistence.repository import InMemoryRepository
from app.models.user import User
from app.models.amenity import Amenity
from app.models.place import Place
from app.models.review import Review


class HBnBFacade:
    def __init__(self):
        self.user_repo = InMemoryRepository()
        self.place_repo = InMemoryRepository()
        self.review_repo = InMemoryRepository()
        self.amenity_repo = InMemoryRepository()

    # Method for creating a user endpoint
    
    def create_user(self, user_data):
        user = User(**user_data)
        self.user_repo.add(user)
        return user

    def get_user(self, user_id):
        return self.user_repo.get(user_id)

    def get_user_by_email(self, email):
        return self.user_repo.get_by_attribute('email', email)

    def get_all_users(self):
        return self.user_repo.get_all()

    def update_user(self, user_id, user_data):
        user = self.user_repo.get(user_id)
        if user:
            user.update(user_data)
        return user

    # Method for creating the amenity endpoints
    
    def create_amenity(self,amenity_data):
        amenity= Amenity(**amenity_data)
        self.amenity_repo.add(amenity)
        return amenity

    def get_amenity(self,amenity_id):
        return self.amenity_repo.get(amenity_id)

    def get_all_amenities(self):
        return self.amenity_repo.get_all()

    def update_amenity(self, amenity_id, amenity_data):
        amenity = self.amenity_repo.get(amenity_id)
        if amenity:
            amenity.update(amenity_data)
        return amenity

    # Method for creating the place endpoints

    def create_place(self, place_data):
    """Create a new Place instance with the provided data"""
        place = Place(**place_data)
    """Add the new place to the repository (database or in-memory store)"""
        self.place_repo.add(place)
    """Return the newly created place object"""
        return place

    def get_place(self, place_id):
    """Check if a place ID was provided"""
        if not place_id:
        """If no ID is given, return None"""
            return None
        else:
        """Otherwise, retrieve and return the place from the repository"""
            return self.place_repo.get(place_id)

    def get_all_places(self):
    """Retrieve all places from the repository"""
        places = self.place_repo.get_all()
    """Return the list of places"""
        return places

    def update_place(self, place_id, place_data):
    """Retrieve the place to update by its ID"""
        place = self.place_repo.get(place_id)

    """If the place does not exist, return None"""
        if not place:
            return None

    """Update the place object with the new data"""
        place.update(place_data)
    """Update the repository with the modified place"""
        self.place_repo.update(place, place_data)
    """Return the updated place object"""
        return place
    
     #  Method for creating a review endpoints
    
    def create_review(self, review_data):
    """Create a new Review instance with the provided data"""
        review = Review(**review_data)
    """Add the new review to the repository (database or in-memory store)"""
        self.review_repo.add(review)
    """Return the newly created review object"""
        return review

    def get_review(self, review_id):
    """
        get_review
        retrieve a review by its ID
    
        The ID of the review to retrieve
        returns: the review objec correspond to ID
    """
        return self.review_repo.get(review_id)

    def get_all_reviews(self):
    """Retrieve all reviews from the repository"""
        reviews = self.review_repo.get_all()
    """Return the list of reviews"""
        return reviews

    def get_reviews_by_place(self, place_id):
    """
        get reviews by place
        retrieve all reviews for a specific place

        The ID of the place to retrieve reviews for
        returns: A list off all the review object for
        specified place
    """
        return self_review_repo.get_by_attribute("place_id", place_id)

    def update_review(self, review_id, review_data):
    """Retrieve the review to update by its ID"""
        review = self.review_repo.get(review_id)

    """If the review does not exist, return None"""
        if not review:
            return None

    """Update the review object with the new data"""
        review.update(review_data)
    """Update the repository with the modified review"""
        self.review_repo.update(review, review_data)
    """Return the updated review object"""
        return review
    
    def delete_review(self, review_id):
        """
        delete_review
        Delete a review by its ID

        The ID of the review to delete
        True if the review was deleted, otherwise False
        
        """
        return self.review_repo.delete(review_id)
