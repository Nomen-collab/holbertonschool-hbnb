from flask_restx import Namespace, Resource, fields
from app.services.facade import HBnBFacade # Importez directement HBnBFacade
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

# Modifié : Ajout de cors_origins='*'
api = Namespace('places', description='Place operations', cors_origins='*')

# Define the models for related entities
# Note: Ces modèles sont pour la documentation de la sortie, pas l'entrée direct.
amenity_model = api.model('PlaceAmenity', {
    'id': fields.String(description='Amenity ID'),
    'name': fields.String(description='Name of the amenity')
})

user_model = api.model('PlaceUser', {
    'id': fields.String(description='User ID'),
    'first_name': fields.String(description='First name of the owner'),
    'last_name': fields.String(description='Last name of the owner'),
    'email': fields.String(description='Email of the owner')
})

# Define the place model for input validation and documentation
# Le modèle d'entrée doit contenir tous les champs que le client envoie
place_input_model = api.model('PlaceInput', {
    'title': fields.String(required=True, description='Title of the place'),
    'description': fields.String(description='Description of the place'),
    'number_rooms': fields.Integer(required=True, description='Number of rooms', min=1),
    'number_bathrooms': fields.Integer(required=True, description='Number of bathrooms', min=0),
    'max_guests': fields.Integer(required=True, description='Maximum number of guests', min=1),
    'price_by_night': fields.Float(required=True, description='Price per night', min=0),
    'latitude': fields.Float(description='Latitude of the place', min=-90, max=90),
    'longitude': fields.Float(description='Longitude of the place', min=-180, max=180),
    # owner_id ne doit PAS être dans l'input_model car il est déduit du JWT
    'amenity_ids': fields.List(fields.String, description="List of amenity ID's to associate with the place", required=False) # Rendu optionnel
})

# Modèle pour la sortie d'un Place (avec les objets imbriqués)
place_output_model = api.model('PlaceOutput', {
    'id': fields.String(description='Place ID'),
    'title': fields.String(description='Title of the place'),
    'description': fields.String(description='Description of the place'),
    'number_rooms': fields.Integer(description='Number of rooms'),
    'number_bathrooms': fields.Integer(description='Number of bathrooms'),
    'max_guests': fields.Integer(description='Maximum number of guests'),
    'price_by_night': fields.Float(description='Price per night'),
    'latitude': fields.Float(description='Latitude of the place'),
    'longitude': fields.Float(description='Longitude of the place'),
    'owner_id': fields.String(description='ID du propriétaire (pour la simplicité)'), # Change to owner_id
    'amenities': fields.List(fields.Nested(amenity_model), description='List of amenities'),
    'reviews': fields.List(fields.String, description='List of review IDs for the place'), # Assuming review IDs for now
    'created_at': fields.DateTime(dt_format='iso8601'),
    'updated_at': fields.DateTime(dt_format='iso8601')
})


# Initialisation de la façade
facade = HBnBFacade()

@api.route('') # C'est la route correcte pour une création sans ID dans l'URL
class PlaceList(Resource):
    @api.expect(place_input_model) # Utilisez place_input_model ici
    @api.response(201, 'Place successfully created', model=place_output_model) # Spécifiez le modèle de sortie
    @api.response(400, 'Invalid input data')
    @jwt_required()
    @api.doc(security='Bearer Auth')
    def post(self):
        """Register a new place"""
        try:
            current_user_id = get_jwt_identity()
            place_data = api.payload
            
            # Ajoutez l'user_id extrait du JWT au payload pour la façade
            # Le 'owner_id' est géré dans la façade si non explicitement fourni
            place_data['user_id'] = current_user_id 
            
            # Appelez la méthode de la façade avec UN SEUL argument (place_data)
            new_place = facade.create_place(place_data)

            # Il faut s'assurer que .to_dict() du modèle Place renvoie toutes les données
            # attendues par place_output_model, y compris les relations chargées
            # (amenities, reviews, et owner).
            # Sinon, vous devrez construire le dictionnaire de sortie ici.
            return new_place.to_dict(), 201

        except ValueError as e: # Capture les erreurs de validation spécifiques de la façade
            api.abort(400, str(e))
        except Exception as e:
            api.abort(500, f"An unexpected error occurred: {str(e)}")


    @api.response(200, 'List of places retrieved successfully', model=api.model('PlaceListOutput', {
        'places': fields.List(fields.Nested(place_output_model), description='List of places')
    }))
    def get(self):
        """Retrieve a list of all places"""
        places = facade.get_all_places()
        
        # Pour le GET, il faut aussi charger les relations si elles doivent apparaître dans le to_dict()
        # Ou modifier to_dict() pour qu'il ne charge que les IDs si c'est ce que place_output_model attend pour les relations.
        # Pour une sortie complète, assurez-vous que les relations sont chargées (e.g., lazy='joined' dans le modèle)
        # ou chargez-les explicitement ici (ex: place_repo.get_all_with_relations()).

        # Pour le moment, to_dict() dans Place ne retourne pas owner ni amenities.
        # Il faudra l'adapter pour correspondre à place_output_model.
        # Voici un exemple si vous voulez construire la sortie ici :
        output_places = []
        for place in places:
            place_dict = place.to_dict()
            
            # Récupérer l'objet propriétaire
            owner = facade.get_user(place.owner_id)
            if owner:
                place_dict['owner'] = owner.to_dict() # Assurez-vous que user.to_dict() existe
            else:
                place_dict['owner'] = None # Ou une valeur par défaut

            # Récupérer les agréments associés
            place_dict['amenities'] = [amenity.to_dict() for amenity in place.amenities] # Assurez-vous que amenity.to_dict() existe
            
            # Récupérer les reviews (ici on suppose juste les IDs, comme dans votre modèle de sortie)
            place_dict['reviews'] = [review.id for review in place.reviews] # Assurez-vous que review.id est accessible
            
            output_places.append(place_dict)
            
        return {'places': output_places}, 200

@api.route('/<string:place_id>')
@api.param('place_id', 'L\'identifiant unique du lieu')
class PlaceResource(Resource):
    @api.response(200, 'Place details retrieved successfully', model=place_output_model)
    @api.response(404, 'Place not found')
    def get(self, place_id):
        """Get place details by ID"""
        place = facade.get_place(place_id)
        if not place:
            api.abort(404, 'Place not found')

        # Adaptez la sortie pour qu'elle corresponde à place_output_model
        place_dict = place.to_dict()
        owner = facade.get_user(place.owner_id)
        if owner:
            place_dict['owner'] = owner.to_dict()
        else:
            place_dict['owner'] = None

        place_dict['amenities'] = [amenity.to_dict() for amenity in place.amenities]
        place_dict['reviews'] = [review.id for review in place.reviews]

        return place_dict, 200

    @api.expect(place_input_model) # Utilisez place_input_model pour l'entrée PUT
    @api.response(200, 'Place updated successfully', model=place_output_model)
    @api.response(404, 'Place not found')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Unauthorized - not the owner or admin')
    @jwt_required()
    @api.doc(security='Bearer Auth')
    def put(self, place_id):
        """Update a place's information"""
        current_user_id = get_jwt_identity()
        place = facade.get_place(place_id)
        if not place:
            api.abort(404, 'Place not found')

        claims = get_jwt()
        is_admin = claims.get('is_admin', False)
        if not is_admin and place.owner_id != current_user_id:
            api.abort(403, 'Unauthorized - you can only modify your own places (or be admin)')

        place_data = api.payload
        # La facade gère maintenant amenity_ids à l'intérieur de place_data
        try:
            updated_place = facade.update_place(place_id, place_data)
            
            # Adaptez la sortie pour qu'elle corresponde à place_output_model
            updated_place_dict = updated_place.to_dict()
            owner = facade.get_user(updated_place.owner_id)
            if owner:
                updated_place_dict['owner'] = owner.to_dict()
            else:
                updated_place_dict['owner'] = None
            updated_place_dict['amenities'] = [amenity.to_dict() for amenity in updated_place.amenities]
            updated_place_dict['reviews'] = [review.id for review in updated_place.reviews]

            return updated_place_dict, 200
        except ValueError as e:
            api.abort(400, str(e))
        except Exception as e:
            api.abort(500, f"An unexpected error occurred: {str(e)}")

    @api.response(204, 'Place deleted successfully')
    @api.response(404, 'Place not found')
    @api.response(403, 'Unauthorized - not the owner or admin')
    @jwt_required()
    @api.doc(security='Bearer Auth')
    def delete(self, place_id):
        """Delete a place"""
        current_user_id = get_jwt_identity()
        place = facade.get_place(place_id)
        if not place:
            api.abort(404, 'Place not found')

        claims = get_jwt()
        is_admin = claims.get('is_admin', False)
        if not is_admin and place.owner_id != current_user_id:
            api.abort(403, 'Unauthorized - you can only delete your own places (or be admin)')

        facade.delete_place(place_id)
        return '', 204
