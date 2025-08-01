from flask_restx import Namespace, Resource, fields
from app.services import facade
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
# Note: amenities ici est une liste de IDs pour l'entrée
place_model = api.model('Place', {
    'title': fields.String(required=True, description='Title of the place'),
    'description': fields.String(description='Description of the place'),
    'number_rooms': fields.Integer(required=True, description='Number of rooms', min=1), # Ajouté
    'number_bathrooms': fields.Integer(required=True, description='Number of bathrooms', min=0), # Ajouté
    'max_guests': fields.Integer(required=True, description='Maximum number of guests', min=1), # Ajouté
    'price_by_night': fields.Float(required=True, description='Price per night', min=0), # Ajouté
    'latitude': fields.Float(description='Latitude of the place', min=-90, max=90), # Rendu optionnel pour l'entrée si non requis
    'longitude': fields.Float(description='Longitude of the place', min=-180, max=180), # Rendu optionnel pour l'entrée si non requis
    # owner_id ne devrait PAS être dans le modèle d'entrée pour POST (il est déduit du JWT)
    'amenity_ids': fields.List(fields.String, description="List of amenity ID's to associate with the place") # Renommé pour clarté
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
    'owner': fields.Nested(user_model, description='Owner details'), # Imbrique le modèle utilisateur
    'amenities': fields.List(fields.Nested(amenity_model), description='List of amenities'), # Imbrique la liste des aménités
    'reviews': fields.List(fields.String, description='List of review IDs for the place') # Ou un modèle de review simple
})


@api.route('/')
class PlaceList(Resource):
    @api.expect(place_model)
    @api.response(201, 'Place successfully created')
    @api.response(400, 'Invalid input data')
    @jwt_required()
    @api.doc(security='Bearer Auth') # Ajout de security='Bearer Auth'
    def post(self):
        """Register a new place"""
        try:
            current_user_id = get_jwt_identity()
            place_data = api.payload
            place_data['owner_id'] = current_user_id # Set the owner_id from JWT (security)

            # Extraire les IDs d'amenities si fournis
            amenity_ids = place_data.pop('amenity_ids', []) # Remove from place_data, use separately

            new_place = facade.create_place(place_data, amenity_ids) # Passer amenity_ids à facade

            return new_place.to_dict(), 201
        except Exception as e:
            api.abort(400, str(e)) # Utilisation de api.abort

    @api.response(200, 'List of places retrieved successfully', model=place_output_model) # Spécifie le modèle de sortie
    def get(self):
        """Retrieve a list of all places"""
        places = facade.get_all_places()
        # Assurez-vous que place.to_dict() retourne aussi owner et amenities sous forme d'objets ou IDs
        # selon ce que place_output_model attend.
        # Si to_dict() ne le fait pas, vous devrez construire la réponse ici.
        return [place.to_dict() for place in places], 200

@api.route('/<string:place_id>') # Spécifiez le type
class PlaceResource(Resource):
    @api.response(200, 'Place details retrieved successfully', model=place_output_model) # Spécifie le modèle de sortie
    @api.response(404, 'Place not found')
    def get(self, place_id):
        """Get place details by ID"""
        place = facade.get_place(place_id)
        if not place:
            api.abort(404, 'Place not found') # Utilisation de api.abort

        return place.to_dict(), 200

    @api.expect(place_model)
    @api.response(200, 'Place updated successfully')
    @api.response(404, 'Place not found')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Unauthorized - not the owner or admin') # Message mis à jour
    @jwt_required()
    @api.doc(security='Bearer Auth') # Ajout de security='Bearer Auth'
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
        amenity_ids = place_data.pop('amenity_ids', None) # Extraire amenities IDs si présents pour la mise à jour

        try:
            updated_place = facade.update_place(place_id, place_data, amenity_ids) # Passer amenity_ids
            return updated_place.to_dict(), 200
        except Exception as e:
            api.abort(400, str(e))

    @api.response(204, 'Place deleted successfully') # 204 No Content
    @api.response(404, 'Place not found')
    @api.response(403, 'Unauthorized - not the owner or admin')
    @jwt_required()
    @api.doc(security='Bearer Auth') # Ajout de security='Bearer Auth'
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
