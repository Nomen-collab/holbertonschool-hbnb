import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from app import db

Base = declarative_base()

class BaseModel(db.Model):
    """Basic class for all models with common features"""
    
    __abstract__ = True
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def save(self):
        """Save object in database"""
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        """Deletes the object from the database"""
        db.session.delete(self)
        db.session.commit()
    
    def update(self, **kwargs):
        """Updates object attributes"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        """Convert object to dictionary"""
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            **{k: v for k, v in self.__dict__.items() 
               if not k.startswith('_') and k not in ['created_at', 'updated_at', 'id']}
        }

