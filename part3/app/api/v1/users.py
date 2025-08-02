from flask_restx import Namespace, Resource, fields
from app.services import facade
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, verify_jwt_in_request # Ajout de verify_jwt_in_request

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
    # @jwt_required()  <--- TOUJOURS ABSENT ICI, C'EST CORRECT
    @api.doc(security='Bearer Auth') # Ceci reste pour la documentation Swagger, mais ne force plus l'auth ici.
    def post(self):
        """Register a new user (admin check is handled internally if needed for subsequent users)"""
        user_data = api.payload

        is_request_admin = user_data.get('is_admin', False)
        current_user_is_admin = False

        # Tente de vérifier si un jeton est présent et valide de manière optionnelle.
        # Cela permet d'appeler get_jwt() sans lever de RuntimeError si aucun jeton n'est présent.
        try:
            verify_jwt_in_request(optional=True)
            claims = get_jwt()
            current_user_is_admin = claims.get('is_admin', False)
        except RuntimeError:
            # Cette exception ne devrait plus se produire grâce à optional=True,
            # mais elle est gardée comme précaution.
            current_user_is_admin = False
        except Exception as e:
            # Gérer d'autres exceptions potentielles de JWT ici si nécessaire
            print(f"Erreur lors de la vérification JWT optionnelle: {e}")
            current_user_is_admin = False


        # Logique pour la création d'un utilisateur admin :
        # 1. Si la requête tente de créer un admin (is_admin=True)
        # 2. Et que l'utilisateur actuel (celui qui fait la requête) n'est PAS un admin
        # 3. Alors, on vérifie si la base de données est vide.
        #    Si elle est vide, on permet la création du premier admin.
        #    Si elle n'est pas vide, on refuse (car seuls les admins peuvent créer d'autres admins).
        
        # Obtenir la liste de tous les utilisateurs pour vérifier si la DB est vide
        all_users = facade.get_all_users()

        if is_request_admin and not current_user_is_admin:
            if len(all_users) == 0:
                # Permettre la création du premier admin si la DB est vide et qu'il n'y a pas de token admin.
                # L'utilisateur doit s'enregistrer avec 'is_admin': true.
                pass
            else:
                # La DB n'est pas vide, et l'utilisateur n'est pas admin, donc il ne peut pas créer un admin.
                api.abort(403, 'Admin privileges required to set a user as admin or create subsequent admin users.')
        elif is_request_admin and current_user_is_admin:
            # Un admin existant crée un nouvel admin, c'est autorisé.
            pass
        # else:
            # Si is_request_admin est False (création d'un utilisateur normal), ou si current_user_is_admin est True
            # (admin crée n'importe qui), la logique continue.

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
