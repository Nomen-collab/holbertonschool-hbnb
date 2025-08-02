from app.models.user import User
from app.models.place import Place
from app.models.review import Review
from app.models.amenity import Amenity

from app.services.repositories.user_repository import UserRepository
from app.services.repositories.place_repository import PlaceRepository
from app.services.repositories.review_repository import ReviewRepository
from app.services.repositories.amenity_repository import AmenityRepository


class HBnBFacade:
    def __init__(self):
        self.user_repo = UserRepository()
        self.place_repo = PlaceRepository()
        self.review_repo = ReviewRepository()
        self.amenity_repo = AmenityRepository()

    # --- User operations ---
    def create_user(self, user_data):
        """
        Crée une nouvelle instance User, hache le mot de passe et l'ajoute au dépôt.
        :param user_data: Dictionnaire contenant les données de l'utilisateur (doit inclure 'password').
        :return: L'objet User créé.
        :raises ValueError: Si l'email existe déjà ou les données sont invalides.
        """
        if self.user_repo.get_user_by_email(user_data.get('email')):
            raise ValueError("Cet email est déjà enregistré.")

        user = User(**user_data)
        if 'password' in user_data:
            user.set_password(user_data['password'])
            
        self.user_repo.add(user)
        return user

    def get_user(self, user_id):
        """Récupère un utilisateur par ID."""
        return self.user_repo.get(user_id)

    def get_user_by_email(self, email):
        """Récupère un utilisateur par email."""
        return self.user_repo.get_user_by_email(email)

    def get_all_users(self):
        """Récupère tous les utilisateurs."""
        return self.user_repo.get_all()

    def update_user(self, user_id, user_data):
        """
        Met à jour un utilisateur par ID.
        :param user_id: ID de l'utilisateur à mettre à jour.
        :param user_data: Dictionnaire des données à mettre à jour.
        :return: L'objet User mis à jour, ou None si non trouvé.
        :raises ValueError: Si l'email est déjà pris par un autre utilisateur.
        """
        user = self.user_repo.get(user_id)
        if not user:
            return None

        if 'email' in user_data and user_data['email'] != user.email:
            if self.user_repo.get_user_by_email(user_data['email']):
                raise ValueError("Cet email est déjà enregistré par un autre utilisateur.")

        if 'password' in user_data and user_data['password']:
            user.set_password(user_data['password'])
            
        self.user_repo.update(user_id, user_data)
        return self.user_repo.get(user_id)

    def delete_user(self, user_id):
        """Supprime un utilisateur par ID."""
        return self.user_repo.delete(user_id)

    # --- Amenity operations ---
    def create_amenity(self, amenity_data):
        """Crée une nouvelle instance Amenity et l'ajoute au dépôt."""
        if 'name' not in amenity_data or not amenity_data['name']:
            raise ValueError("Le nom de l'agrément est requis.")
        
        amenity = Amenity(**amenity_data)
        self.amenity_repo.add(amenity)
        return amenity

    def get_amenity(self, amenity_id):
        """Récupère un agrément par ID."""
        return self.amenity_repo.get(amenity_id)

    def get_all_amenities(self):
        """Récupère tous les agréments."""
        return self.amenity_repo.get_all()

    def update_amenity(self, amenity_id, amenity_data):
        """Met à jour un agrément par ID."""
        amenity = self.amenity_repo.get(amenity_id)
        if amenity:
            self.amenity_repo.update(amenity_id, amenity_data)
            return self.amenity_repo.get(amenity_id)
        return None

    def delete_amenity(self, amenity_id):
        """Supprime un agrément par ID."""
        return self.amenity_repo.delete(amenity_id)

    # --- Place operations ---
    def create_place(self, place_data):
        """
        Crée une nouvelle instance Place et l'ajoute au dépôt, en gérant les amenities.
        :param place_data: Dictionnaire contenant toutes les données du lieu, y compris 'amenity_ids' si présents.
        :return: L'objet Place créé.
        :raises ValueError: Si des champs requis sont manquants ou les IDs de référence sont invalides.
        """
        required_fields = ['title', 'user_id', 'price_by_night', 'number_rooms', 'number_bathrooms', 'max_guests']
        for field in required_fields:
            if field not in place_data or place_data[field] is None:
                raise ValueError(f"Champ requis manquant ou vide pour la création du lieu: '{field}'")
        
        # Extraire amenity_ids du dictionnaire place_data avant de créer l'objet Place
        amenity_ids = place_data.pop('amenity_ids', [])

        user = self.user_repo.get(place_data['user_id'])
        if not user:
            raise ValueError(f"L'utilisateur (créateur) avec l'ID '{place_data['user_id']}' n'existe pas.")

        if 'owner_id' not in place_data or place_data['owner_id'] is None:
            place_data['owner_id'] = place_data['user_id']
        else:
            owner = self.user_repo.get(place_data['owner_id'])
            if not owner:
                raise ValueError(f"Le propriétaire avec l'ID '{place_data['owner_id']}' n'existe pas.")

        place = Place(**place_data) # Crée l'objet Place SANS amenity_ids
        
        # Ajouter les amenities après la création du lieu
        if amenity_ids:
            amenities = []
            for amenity_id in amenity_ids:
                amenity = self.amenity_repo.get(amenity_id)
                if not amenity:
                    raise ValueError(f"L'agrément avec l'ID '{amenity_id}' n'existe pas.")
                amenities.append(amenity)
            place.amenities = amenities # Assurez-vous que votre modèle Place a cette relation many-to-many

        self.place_repo.add(place) # Ceci persistera le lieu et ses relations amenities
        return place

    def get_place(self, place_id):
        """Récupère un lieu par ID."""
        return self.place_repo.get(place_id)

    def get_all_places(self):
        """Récupère tous les lieux."""
        return self.place_repo.get_all()

    def update_place(self, place_id, place_data):
        """
        Met à jour un lieu par ID, en gérant les amenities.
        :param place_id: ID du lieu à mettre à jour.
        :param place_data: Dictionnaire des données à mettre à jour, y compris 'amenity_ids' si présents.
        :return: L'objet Place mis à jour, ou None si non trouvé.
        :raises ValueError: Si des IDs de référence (user_id, owner_id, amenity_ids) sont invalides.
        """
        place = self.place_repo.get(place_id)
        if not place:
            return None

        # Extraire amenity_ids du dictionnaire place_data avant la mise à jour
        amenity_ids = place_data.pop('amenity_ids', None)

        if 'user_id' in place_data and place_data['user_id']:
            user = self.user_repo.get(place_data['user_id'])
            if not user:
                raise ValueError(f"L'utilisateur (créateur) avec l'ID '{place_data['user_id']}' n'existe pas.")
        if 'owner_id' in place_data and place_data['owner_id']:
            owner = self.user_repo.get(place_data['owner_id'])
            if not owner:
                raise ValueError(f"Le propriétaire avec l'ID '{place_data['owner_id']}' n'existe pas.")
        
        # Mettre à jour les attributs de base du lieu
        self.place_repo.update(place_id, place_data)

        # Gérer la mise à jour des amenities
        if amenity_ids is not None: # Seulement si amenity_ids est explicitement fourni pour la mise à jour
            current_amenities = []
            for amenity_id in amenity_ids:
                amenity = self.amenity_repo.get(amenity_id)
                if not amenity:
                    raise ValueError(f"L'agrément avec l'ID '{amenity_id}' n'existe pas.")
                current_amenities.append(amenity)
            place.amenities = current_amenities # Met à jour la relation (remplace les anciennes)
            self.place_repo.db_session.commit() # Commit la mise à jour des relations

        return self.place_repo.get(place_id) # Récupère le lieu mis à jour pour s'assurer que les relations sont chargées

    def delete_place(self, place_id):
        """Supprime un lieu par ID."""
        return self.place_repo.delete(place_id)

    # --- Review operations ---
    def create_review(self, review_data):
        """
        Crée une nouvelle instance Review et l'ajoute au dépôt.
        :param review_data: Dictionnaire contenant les données de la critique.
        :return: L'objet Review créé.
        :raises ValueError: Si des champs requis sont manquants ou les IDs de référence sont invalides.
        """
        required_fields = ['text', 'rating', 'user_id', 'place_id']
        for field in required_fields:
            if field not in review_data or review_data[field] is None:
                raise ValueError(f"Champ requis manquant ou vide pour la création de la critique: '{field}'")

        user = self.user_repo.get(review_data['user_id'])
        if not user:
            raise ValueError(f"L'utilisateur avec l'ID '{review_data['user_id']}' n'existe pas.")
        place = self.place_repo.get(review_data['place_id'])
        if not place:
            raise ValueError(f"Le lieu avec l'ID '{review_data['place_id']}' n'existe pas.")

        review = Review(**review_data)
        self.review_repo.add(review)
        return review

    def get_review(self, review_id):
        """Récupère une critique par ID."""
        return self.review_repo.get(review_id)

    def get_all_reviews(self):
        """Récupère toutes les critiques."""
        return self.review_repo.get_all()

    def update_review(self, review_id, review_data):
        """
        Met à jour une critique par ID.
        :param review_id: ID de la critique à mettre à jour.
        :param review_data: Dictionnaire des données à mettre à jour.
        :return: L'objet Review mis à jour, ou None si non trouvé.
        :raises ValueError: Si des IDs de référence (user_id, place_id) sont invalides.
        """
        review = self.review_repo.get(review_id)
        if not review:
            return None

        if 'user_id' in review_data and review_data['user_id']:
            user = self.user_repo.get(review_data['user_id'])
            if not user:
                raise ValueError(f"L'utilisateur avec l'ID '{review_data['user_id']}' n'existe pas.")
        if 'place_id' in review_data and review_data['place_id']:
            place = self.place_repo.get(review_data['place_id'])
            if not place:
                raise ValueError(f"Le lieu avec l'ID '{review_data['place_id']}' n'existe pas.")

        self.review_repo.update(review_id, review_data)
        return self.review_repo.get(review_id)

    def delete_review(self, review_id):
        """Supprime une critique par ID."""
        return self.review_repo.delete(review_id)
