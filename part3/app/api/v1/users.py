from flask_restx import Namespace, Resource, fields
from app.services import facade
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt # Importez get_jwt pour accéder aux claims du JWT

api = Namespace('users', description='User operations')

# Define the user model for input validation and documentation
user_model = api.model('User', {
    'first_name': fields.String(required=True, description='First name of the user', max_length=50),
    'last_name': fields.String(required=True, description='Last name of the user', max_length=50),
    'email': fields.String(required=True, description='Email of the user', pattern=r'^[^@]+@[^@]+\.[^@]+$'),
    'password': fields.String(required=True, description='password of the user', min_length=6)
})

# Define a model for user creation (can be the same as user_model for simplicity if no specific differences)
# It's good practice to have a separate model if input requirements differ for creation vs. update/display
user_creation_model = api.model('UserCreation', {
    'first_name': fields.String(required=True, description='First name of the user', max_length=50),
    'last_name': fields.String(required=True, description='Last name of the user', max_length=50),
    'email': fields.String(required=True, description='Email of the user', pattern=r'^[^@]+@[^@]+\.[^@]+$'),
    'password': fields.String(required=True, description='password of the user', min_length=6)
})


@api.route('/')
class UserList(Resource):
    @api.expect(user_creation_model, validate=True) # Utilisez user_creation_model pour la création
    @api.response(201, 'User successfully created')
    @api.response(400, 'Email already registered')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Admin privileges required')
    @jwt_required() # <--- Gardez cette ligne pour exiger un JWT valide
    @api.doc(security='Bearer') # Indique à Swagger que cette route nécessite un token Bearer
    def post(self):
        """Register a new user - ADMIN ONLY"""
        # Récupère les claims du JWT pour vérifier si l'utilisateur est admin
        claims = get_jwt()
        if not claims.get('is_admin'):
            api.abort(403, 'Admin privileges required') # Utilisation de api.abort pour les erreurs RestX

        user_data = api.payload

        # Vérification de l'unicité de l'email
        existing_user = facade.get_user_by_email(user_data['email'])

        if existing_user:
            api.abort(400, 'Email already registered') # Utilisation de api.abort

        new_user = facade.create_user(user_data)

        # Le hachage du mot de passe devrait idéalement être géré dans facade.create_user
        # ou au niveau du modèle avant d'être persisté, mais je le garde ici si c'est votre structure actuelle.
        if 'password' in user_data:
            new_user.hash_password(user_data['password'])

        return {'id': new_user.id, 'first_name': new_user.first_name, 'last_name': new_user.last_name, 'email': new_user.email}, 201

    @api.response(200, 'List of users retrieved successfully')
    @jwt_required() # <--- Ajouté pour protéger la route GET /users aussi
    @api.doc(security='Bearer') # Indique à Swagger que cette route nécessite un token Bearer
    def get(self):
        """Get all users"""
        # Optionnel: vous pouvez ajouter une vérification is_admin ici aussi si seuls les admins peuvent voir tous les utilisateurs
        # claims = get_jwt()
        # if not claims.get('is_admin'):
        #     api.abort(403, 'Admin privileges required to view all users')

        users = facade.get_all_users()
        return [{'id': user.id, 'first_name': user.first_name, 'last_name': user.last_name, 'email': user.email} for user in users], 200

@api.route('/<string:user_id>') # Spécifiez le type de l'ID pour une meilleure clarté et validation
class UserResource(Resource):
    @api.response(200, 'User details retrieved successfully')
    @api.response(404, 'User not found')
    @jwt_required() # <--- Protéger la lecture d'un seul utilisateur
    @api.doc(security='Bearer')
    def get(self, user_id):
        """Get user details by ID"""
        # Optionnel: l'utilisateur ne peut voir que son propre profil s'il n'est pas admin
        # current_user_id = get_jwt_identity()
        # claims = get_jwt()
        # if not claims.get('is_admin') and current_user_id != user_id:
        #     api.abort(403, 'Unauthorized: You can only view your own profile.')

        user = facade.get_user(user_id)
        if not user:
            api.abort(404, 'User not found') # Utilisation de api.abort
        return {'id': user.id, 'first_name': user.first_name, 'last_name': user.last_name, 'email': user.email}, 200

    @api.expect(user_model, validate=True)
    @api.response(200, 'User successfully updated')
    @api.response(404, 'User not found')
    @api.response(400, 'Invalid input data or Email already registered') # Unifier les messages d'erreur
    @api.response(403, 'Unauthorized - you can only modify your own profile')
    @jwt_required() # Protéger la mise à jour d'un utilisateur
    @api.doc(security='Bearer')
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
        if 'email' in user_data:
            existing_user = facade.get_user_by_email(user_data['email'])
            if existing_user and existing_user.id != user_id:
                api.abort(400, 'Email already registered') # Utilisation de api.abort

        facade.update_user(user_id, user_data)
        updated_user = facade.get_user(user_id)
        return {'id': updated_user.id, 'first_name': updated_user.first_name, 'last_name': updated_user.last_name, 'email': updated_user.email}, 200

    @api.response(204, 'User successfully deleted')
    @api.response(404, 'User not found')
    @api.response(403, 'Admin privileges required')
    @jwt_required() # Protéger la suppression
    @api.doc(security='Bearer')
    def delete(self, user_id):
        """Delete a user - ADMIN ONLY"""
        claims = get_jwt()
        if not claims.get('is_admin'):
            api.abort(403, 'Admin privileges required')

        user = facade.get_user(user_id)
        if not user:
            api.abort(404, 'User not found')

        facade.delete_user(user_id)
        return '', 204 # Réponse 204 No Content pour une suppression réussie
