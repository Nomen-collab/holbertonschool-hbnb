from flask_restx import Namespace, Resource, fields
from app.services import facade
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

# Modifié : Ajout de cors_origins='*'
api = Namespace('amenities', description='Amenity operations', cors_origins='*')

# Define the amenity model for input validation and documentation
amenity_model = api.model('Amenity', {
    'name': fields.String(required=True, description='Name of the amenity', max_length=100)
})

@api.route('/')
class AmenityList(Resource):
    @api.expect(amenity_model, validate=True)
    @api.response(201, 'Amenity successfully created')
    @api.response(400, 'Invalid input data or Amenity name already exists') # Message unifié
    @api.response(403, 'Admin privileges required')
    @jwt_required()
    @api.doc(security='Bearer Auth') # Ajout de security='Bearer Auth'
    def post(self):
        """Register a new amenity - ADMIN ONLY"""
        claims = get_jwt()
        if not claims.get('is_admin'):
            api.abort(403, 'Admin privileges required')

        amenity_data = api.payload

        # Vérification de l'unicité du nom de l'amenity
        existing_amenity = facade.get_amenity_by_name(amenity_data['name'])
        if existing_amenity:
            api.abort(400, 'Amenity with this name already exists')

        new_amenity = facade.create_amenity(amenity_data)
        return {
            "id": new_amenity.id,
            "name": new_amenity.name
        }, 201

    @api.response(200, 'List of amenities retrieved successfully')
    @api.doc(security='Bearer Auth', params={'Authorization': {'description': 'Optionnel: Jeton JWT pour l\'authentification'}}) # Peut être public ou protégé
    def get(self):
        """Retrieve a list of all amenities"""
        amenities = facade.get_all_amenities()
        return [
            {"id": amenity.id, "name": amenity.name}
            for amenity in amenities
        ], 200

@api.route('/<string:amenity_id>') # Spécifiez le type
class AmenityResource(Resource):
    @api.response(200, 'Amenity details retrieved successfully')
    @api.response(404, 'Amenity not found')
    @api.doc(security='Bearer Auth', params={'Authorization': {'description': 'Optionnel: Jeton JWT pour l\'authentification'}})
    def get(self, amenity_id):
        """Get amenity details by ID"""
        amenity = facade.get_amenity(amenity_id)
        if not amenity:
            api.abort(404, 'Amenity not found')
        return {
            "id": amenity.id,
            "name": amenity.name
        }, 200

    @api.expect(amenity_model, validate=True)
    @api.response(200, 'Amenity updated successfully')
    @api.response(404, 'Amenity not found')
    @api.response(400, 'Invalid input data or Amenity name already exists') # Message unifié
    @api.response(403, 'Admin privileges required')
    @jwt_required()
    @api.doc(security='Bearer Auth') # Ajout de security='Bearer Auth'
    def put(self, amenity_id):
        """Update an amenity's information - ADMIN ONLY"""
        claims = get_jwt()
        if not claims.get('is_admin'):
            api.abort(403, 'Admin privileges required')

        amenity_data = api.payload
        amenity = facade.get_amenity(amenity_id)
        if not amenity:
            api.abort(404, 'Amenity not found')

        # Vérification de l'unicité du nom si le nom est modifié
        if 'name' in amenity_data and amenity_data['name'] != amenity.name:
            existing_amenity = facade.get_amenity_by_name(amenity_data['name'])
            if existing_amenity and existing_amenity.id != amenity_id:
                api.abort(400, 'Amenity with this name already exists')

        updated_amenity = facade.update_amenity(amenity_id, amenity_data)
        return {
            "id": updated_amenity.id,
            "name": updated_amenity.name
        }, 200

    @api.response(204, 'Amenity deleted successfully') # 204 No Content
    @api.response(404, 'Amenity not found')
    @api.response(403, 'Admin privileges required')
    @jwt_required()
    @api.doc(security='Bearer Auth') # Ajout de security='Bearer Auth'
    def delete(self, amenity_id):
        """Delete an amenity - ADMIN ONLY"""
        claims = get_jwt()
        if not claims.get('is_admin'):
            api.abort(403, 'Admin privileges required')

        amenity = facade.get_amenity(amenity_id)
        if not amenity:
            api.abort(404, 'Amenity not found')

        facade.delete_amenity(amenity_id)
        return '', 204
