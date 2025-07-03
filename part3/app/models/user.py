from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.base_model import BaseModel

class User(BaseModel):
    """User model with SQLAlchemy mapping"""
    
    __tablename__ = 'users'
    
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password = Column(String(128), nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    
    # Relationships (defined in Task 8)
    places = relationship("Place", back_populates="owner", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")
    
    def __init__(self, first_name, last_name, email, password, is_admin=False):
        super().__init__()
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.hash_password(password)
        self.is_admin = is_admin
    
    def hash_password(self, password):
        """Hash password with bcrypt"""
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password"""
        return check_password_hash(self.password, password)
    
    def to_dict(self):
        """Converts to dict without exposing the password"""
        data = super().to_dict()
        data.update({
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'is_admin': self.is_admin
        })
        # Never expose the password
        data.pop('password', None)
        return data
    
    def __repr__(self):
        return f'<User {self.email}>'

