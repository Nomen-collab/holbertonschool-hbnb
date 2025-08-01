from flask_restx import Namespace, Resource, fields
from app.services import facade
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

# Modifié : Ajout de cors_origins='*'
api = Namespace('reviews', description='Review operations', cors_origins='*')

# Define the review model for input validation and documentation
review_model = api.model('Review', {
    'text': fields.String(required=True, description='Text of the review'),
    'rating': fields.Integer(required=True, description='Rating of the place (1-5)', min=1, max=5), # Ajout min/max
    # 'user_id' et 'place_id' ne devraient pas être requis dans le payload POST si le JWT les déduit.
    # Ils sont inclus dans la réponse ou pour les PUT/GET par ID.
    'user_id': fields.String(description='ID of the user (auto-set from JWT for POST)'),
    'place_id': fields.String(required=True, description='ID of the place')
})

@api.route('/')
class ReviewList(Resource):
    @api.expect(review_model)
    @api.response(201, 'Review successfully created')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Cannot review your own place or duplicate review')
    @api.response(404, 'Place not found') # Ajout de la réponse 404
    @jwt_required()
    @api.doc(security='Bearer Auth') # Ajout de security='Bearer Auth'
    def post(self):
        """Register a new review"""
        # Utilisation de api.abort pour une meilleure cohérence avec Flask-RestX
        current_user_id = get_jwt_identity()
        review_data = api.payload
        review_data['user_id'] = current_user_id # Set user_id from JWT

        place = facade.get_place(review_data['place_id'])
        if not place:
            api.abort(404, 'Place not found') # Utilisation de api.abort

        if place.owner_id == current_user_id:
            api.abort(403, 'Cannot review your own place') # Utilisation de api.abort

        existing_reviews = facade.get_reviews_by_place(review_data['place_id'])
        for existing_review in existing_reviews:
            if existing_review.user_id == current_user_id:
                api.abort(403, 'You have already reviewed this place') # Utilisation de api.abort

        try:
            review = facade.create_review(review_data)
            return review.to_dict(), 201
        except Exception as e:
            # Gérer les erreurs de validation ou de base de données plus spécifiquement si possible
            api.abort(400, str(e)) # Utilisation de api.abort pour les erreurs 400

    @api.response(200, 'List of reviews retrieved successfully')
    @api.doc(security='Bearer Auth', params={'Authorization': {'description': 'Optionnel: Jeton JWT pour l\'authentification'}}) # La route GET peut être publique ou protégée
    def get(self):
        """Retrieve a list of all reviews"""
        reviews = facade.get_all_reviews()
        return [review.to_dict() for review in reviews], 200

@api.route('/<string:review_id>') # Spécifiez le type pour validation Swagger
class ReviewResource(Resource):
    @api.response(200, 'Review details retrieved successfully')
    @api.response(404, 'Review not found')
    @api.doc(security='Bearer Auth', params={'Authorization': {'description': 'Optionnel: Jeton JWT pour l\'authentification'}})
    def get(self, review_id):
        """Get review details by ID"""
        review = facade.get_review(review_id)
        if not review:
            api.abort(404, 'Review not found')
        return review.to_dict(), 200

    @api.expect(review_model)
    @api.response(200, 'Review updated successfully')
    @api.response(404, 'Review not found')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Unauthorized - not the review author or admin') # Message mis à jour
    @jwt_required()
    @api.doc(security='Bearer Auth') # Ajout de security='Bearer Auth'
    def put(self, review_id):
        """Update a review's information"""
        current_user_id = get_jwt_identity()
        review = facade.get_review(review_id)
        if not review:
            api.abort(404, 'Review not found')

        claims = get_jwt()
        is_admin = claims.get('is_admin', False)
        if not is_admin and review.user_id != current_user_id:
            api.abort(403, 'Unauthorized - you can only modify your own reviews (or be admin)')

        try:
            updated_review = facade.update_review(review_id, api.payload)
            return updated_review.to_dict(), 200
        except Exception as e:
            api.abort(400, str(e))

    @api.response(204, 'Review deleted successfully') # 204 No Content est plus approprié pour DELETE
    @api.response(404, 'Review not found')
    @api.response(403, 'Unauthorized - not the review author or admin') # Message mis à jour
    @jwt_required()
    @api.doc(security='Bearer Auth') # Ajout de security='Bearer Auth'
    def delete(self, review_id):
        """Delete a review"""
        current_user_id = get_jwt_identity()
        review = facade.get_review(review_id)
        if not review:
            api.abort(404, 'Review not found')

        claims = get_jwt()
        is_admin = claims.get('is_admin', False)
        if not is_admin and review.user_id != current_user_id:
            api.abort(403, 'Unauthorized - you can only delete your own reviews (or be admin)')

        facade.delete_review(review_id)
        return '', 204 # Retourne 204 No Content
