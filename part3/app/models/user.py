from app.models.base_model import BaseModel


class User(BaseModel):
    def __init__(self, first_name, last_name, email, password="", is_admin=False):
        super().__init__()

        if len(first_name) > 50:
            raise ValueError("first name too long")
        if len(last_name) > 50:
            raise ValueError("Last name too long")
        if "@" not in email:
            raise ValueError("invalid Email")

        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.is_admin = is_admin


    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


    def hash_password(self, password):
        """hashes the password before storage"""
        from app import bcrypt
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')


    def verify_password(self, password):
        """Verify that the password matches the hashed password"""
        from app import bcrypt
        return bcrypt.check_password_hash(self.password, password)


    def update(self, data):
        """Update user attributes"""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

        self.save()
