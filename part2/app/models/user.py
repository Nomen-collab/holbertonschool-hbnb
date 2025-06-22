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

    def update(self, data):
    """Update user attributes"""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.save()
