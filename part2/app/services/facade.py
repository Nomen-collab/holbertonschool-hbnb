# app/services/facade.py
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

    # User endpoints
    def create_user(self, user_data):
        """Creates a new User instance and adds it to the repository."""
        # Note: Pass user_data directly with **user_data if all fields match constructor
        user = User(**user_data) 
        self.user_repo.add(user)
        return user

    def get_user(self, user_id):
        """Retrieves a user by ID."""
        return self.user_repo.get(user_id)

    def get_user_by_email(self, email):
        """Retrieves a user by email."""
        # Note: get_by_attribute in InMemoryRepository is suitable here
        return self.user_repo.get_by_attribute('email', email)

    def get_all_users(self):
        """Retrieves all users."""
        return self.user_repo.get_all()

    def update_user(self, user_id, user_data):
        """Updates a user by ID."""
        user = self.user_repo.get(user_id)
        if user:
            user.update(user_data)
        return user

    def delete_user(self, user_id):
        """Deletes a user by ID."""
        return self.user_repo.delete(user_id)

    # Amenity endpoints
    def create_amenity(self, amenity_data):
        """Creates a new Amenity instance and adds it to the repository."""
        amenity = Amenity(**amenity_data)
        self.amenity_repo.add(amenity)
        return amenity

    def get_amenity(self, amenity_id):
        """Retrieves an amenity by ID."""
        return self.amenity_repo.get(amenity_id)

    def get_all_amenities(self):
        """Retrieves all amenities."""
        return self.amenity_repo.get_all()

    def update_amenity(self, amenity_id, amenity_data):
        """Updates an amenity by ID."""
        amenity = self.amenity_repo.get(amenity_id)
        if amenity:
            amenity.update(amenity_data)
        return amenity

    def delete_amenity(self, amenity_id):
        """Deletes an amenity by ID."""
        return self.amenity_repo.delete(amenity_id)

    # Place endpoints
    def create_place(self, place_data):
        """Creates a new Place instance and adds it to the repository."""
        owner_id = place_data.get('owner_id')
        if not owner_id:
            raise ValueError("Owner ID is required for a Place.")
        
        owner = self.user_repo.get(owner_id)
        if not owner:
            raise ValueError(f"Owner with ID {owner_id} not found.")

        # Retrieve and validate amenities (if present in payload)
        amenity_ids = place_data.get('amenities', []) # Retrieves the list of amenity IDs
        amenities_objects = []
        for aid in amenity_ids:
            amenity = self.amenity_repo.get(aid)
            if not amenity:
                raise ValueError(f"Amenity with ID {aid} not found.")
            amenities_objects.append(amenity)

        # Prepare arguments for the Place constructor
        place_args = {
            'title': place_data['title'],
            'description': place_data.get('description'), 
            'price': place_data['price'],
            'latitude': place_data['latitude'],
            'longitude': place_data['longitude'],
            'owner': owner, 
            'amenities': amenities_objects 
        }
        
        place = Place(**place_args)
        self.place_repo.add(place)
        return place

    def get_place(self, place_id):
        """Retrieves a place by ID."""
        if not place_id:
            return None
        return self.place_repo.get(place_id)

    def get_all_places(self):
        """Retrieves all places."""
        return self.place_repo.get_all()

    def update_place(self, place_id, place_data):
        """Updates a place by ID."""
        place = self.place_repo.get(place_id)
        if not place:
            return None
        
        # Handle updating the owner (if ID changes)
        if 'owner_id' in place_data:
            new_owner_id = place_data['owner_id']
            new_owner = self.user_repo.get(new_owner_id)
            if not new_owner:
                raise ValueError(f"New owner with ID {new_owner_id} not found.")
            place_data['owner'] = new_owner 
            del place_data['owner_id'] 

        # Handle updating amenities (if the list of IDs changes)
        if 'amenities' in place_data:
            new_amenity_ids = place_data['amenities']
            new_amenities_objects = []
            for aid in new_amenity_ids:
                amenity = self.amenity_repo.get(aid)
                if not amenity:
                    raise ValueError(f"Amenity with ID {aid} not found for update.")
                new_amenities_objects.append(amenity)
            place_data['amenities'] = new_amenities_objects 

        place.update(place_data) 
        return place

    def delete_place(self, place_id):
        """Deletes a place by ID."""
        return self.place_repo.delete(place_id)

    # Review endpoints
    def create_review(self, review_data):
        """Creates a new Review instance and adds it to the repository."""
        user_id = review_data.get('user_id')
        place_id = review_data.get('place_id')
        
        if not user_id:
            raise ValueError("User ID is required for a Review.")
        if not place_id:
            raise ValueError("Place ID is required for a Review.")
        
        user = self.user_repo.get(user_id) 
        place = self.place_repo.get(place_id)
        
        if not user:
            raise ValueError(f"User with ID {user_id} not found.")
        if not place:
            raise ValueError(f"Place with ID {place_id} not found.")
        
        review_args = {
            'text': review_data['text'],
            'rating': review_data['rating'],
            'place': place,  # ✅ Place OBJECT
            'user': user     # ✅ User OBJECT
        }
        
        review = Review(**review_args)
        self.review_repo.add(review)
        return review

    def get_review(self, review_id):
        """Retrieves a review by ID."""
        return self.review_repo.get(review_id)

    def get_all_reviews(self):
        """Retrieves all reviews."""
        return self.review_repo.get_all()

    def get_reviews_by_place(self, place_id):
        """Retrieves all reviews for a specific place."""
        all_reviews = self.review_repo.get_all() 
        filtered_reviews = [review for review in all_reviews if review.place and review.place.id == place_id]
        return filtered_reviews

    def update_review(self, review_id, review_data):
        """Updates a review by ID."""
        review = self.review_repo.get(review_id)
        if not review:
            return None

        if 'user_id' in review_data:
            user = self.user_repo.get(review_data['user_id'])
            if not user:
                raise ValueError(f"User with ID {review_data['user_id']} not found.")
            review_data['user'] = user
            del review_data['user_id']



