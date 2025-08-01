from flask_restx import Namespace, Resource, fields
from app.services import facade
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

# Modifié : Ajout de cors_origins='*' pour gérer les requêtes OPTIONS
api = Namespace('users', description='User operations', cors_origins='*')

# Define the user model for input validation and documentation
user_model = api.model('User', {
    'first_name': fields.String(required=True, description='First name of the user', max_length=50),
    'last_name': fields.String(required=True, description='Last name of the user', max_length=50),
    'email': fields.String(required=True, description='Email of the user', pattern=r'^[^@]+@[^@]+\.[^@]+$'),
    'password': fields.String(required=True, description='password of the user', min_length=6)
})

# Define a model for user creation (can be the same as user_model for simplicity if no specific differences)
user_creation_model = api.model('UserCreation', {
    'first_name': fields.String(required=True, description='First name of the user', max_length=50),
    'last_name': fields.String(required=True, description='Last name of the user', max_length=50),
    'email': fields.String(required=True, description='Email of the user', pattern=r'^[^@]+@[^@]+\.[^@]+$'),
    'password': fields.String(required=True, description='password of the user', min_length=6),
    # IMPORTANT: is_admin ne devrait être présent ici que pour la création du premier admin.
    # Normalement, les utilisateurs classiques ne devraient pas pouvoir définir cela.
    # Pour la création du premier admin, vous devrez temporairement décommenter cette ligne.
    'is_admin': fields.Boolean(description='Is the user an admin?', default=False)
})


@api.route('/')
class UserList(Resource):
    @api.expect(user_creation_model, validate=True)
    @api.response(201, 'User successfully created')
    @api.response(400, 'Email already registered or Invalid input data') # Message unifié
    @api.response(403, 'Admin privileges required')
    @jwt_required()
    # Ajout de security='Bearer Auth' pour lier cette route à la définition de sécurité globale
    @api.doc(security='Bearer Auth')
    def post(self):
        """Register a new user - ADMIN ONLY (temporairement modifié pour le 1er admin)"""
        # Vérification Admin - A COMMENTER TEMPORAIREMENT POUR LE 1ER ADMIN
        claims = get_jwt()
        if not claims.get('is_admin'):
            api.abort(403, 'Admin privileges required')

        user_data = api.payload

        # Vérification de l'unicité de l'email
        existing_user = facade.get_user_by_email(user_data['email'])

        if existing_user:
            api.abort(400, 'Email already registered')

        new_user = facade.create_user(user_data) # Hashage du mot de passe doit être géré dans create_user

        # La réponse ne devrait pas inclure le mot de passe
        return {'id': new_user.id, 'first_name': new_user.first_name, 'last_name': new_user.last_name, 'email': new_user.email, 'is_admin': new_user.is_admin}, 201

    @api.response(200, 'List of users retrieved successfully')
    @jwt_required()
    @api.doc(security='Bearer Auth') # Ajout de security='Bearer Auth'
    def get(self):
        """Get all users"""
        # Optionnel: vous pouvez ajouter une vérification is_admin ici aussi si seuls les admins peuvent voir tous les utilisateurs
        # claims = get_jwt()
        # if not claims.get('is_admin'):
        #    api.abort(403, 'Admin privileges required to view all users')

        users = facade.get_all_users()
        # Retourne is_admin aussi
        return [{'id': user.id, 'first_name': user.first_name, 'last_name': user.last_name, 'email': user.email, 'is_admin': user.is_admin} for user in users], 200

@api.route('/<string:user_id>')
class UserResource(Resource):
    @api.response(200, 'User details retrieved successfully')
    @api.response(404, 'User not found')
    @jwt_required()
    @api.doc(security='Bearer Auth') # Ajout de security='Bearer Auth'
    def get(self, user_id):
        """Get user details by ID"""
        user = facade.get_user(user_id)
        if not user:
            api.abort(404, 'User not found')
        # Retourne is_admin aussi
        return {'id': user.id, 'first_name': user.first_name, 'last_name': user.last_name, 'email': user.email, 'is_admin': user.is_admin}, 200

    @api.expect(user_model, validate=True)
    @api.response(200, 'User successfully updated')
    @api.response(404, 'User not found')
    @api.response(400, 'Invalid input data or Email already registered')
    @api.response(403, 'Unauthorized - you can only modify your own profile')
    @jwt_required()
    @api.doc(security='Bearer Auth') # Ajout de security='Bearer Auth'
    def put(self, user_id):
        """Update user information"""
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)

        # Seul l'utilisateur lui-même ou un administrateur peut modifier le profil
        if not is_admin and current_user_id != user_id:
            api.abort(403, 'Unauthorized: You can only modify your own profile')

        user_data = api.payload
        user = facade.get_user(user_id)
        if not user:
            api.abort(404, 'User not found')

        # Check if email is being changed and if it's already taken by another user
        if 'email' in user_data and user_data['email'] != user.email: # Check only if email is actually changed
            existing_user = facade.get_user_by_email(user_data['email'])
            if existing_user and existing_user.id != user_id:
                api.abort(400, 'Email already registered')

        facade.update_user(user_id, user_data)
        updated_user = facade.get_user(user_id)
        return {'id': updated_user.id, 'first_name': updated_user.first_name, 'last_name': updated_user.last_name, 'email': updated_user.email, 'is_admin': updated_user.is_admin}, 200

    @api.response(204, 'User successfully deleted')
    @api.response(404, 'User not found')
    @api.response(403, 'Admin privileges required')
    @jwt_required()
    @api.doc(security='Bearer Auth') # Ajout de security='Bearer Auth'
    def delete(self, user_id):
        """Delete a user - ADMIN ONLY"""
        claims = get_jwt()
        if not claims.get('is_admin'):
            api.abort(403, 'Admin privileges required')

        user = facade.get_user(user_id)
        if not user:
            api.abort(404, 'User not found')

        facade.delete_user(user_id)
        return '', 204
