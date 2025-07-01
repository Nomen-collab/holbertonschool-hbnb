from abc import ABC, abstractmethod
from typing import List, Optional, Type, TypeVar
from sqlalchemy.orm import Session
from app import db

T = TypeVar('T')

class Repository(ABC):
    @abstractmethod
    def add(self, obj):
        pass

    @abstractmethod
    def get(self, obj_id: str):
        pass

    @abstractmethod
    def get_all(self) -> List:
        pass

    @abstractmethod
    def update(self, obj_id: str, data: dict):
        pass

    @abstractmethod
    def delete(self, obj_id: str):
        pass


class SQLAlchemyRepository(Repository):

    def __init__(self, model: Type[T]):
        self.model = model
        self.session: Session = db.session

    def add(self, obj: T) -> T:
        """Adding an objet to the database"""
        try:
            self.session(obj)
            self.session.commit()
            return obj
        except Exception as e:
            self.session.rollback()
            raise e

    def get(self, obj_id: str) -> Optional[T]:
        """recover an object by ID"""
        return self.session.query(self.model).filter_by(id=obj_id).first()

    def get_all(self) -> List[T]
        """recover all the objects"""
        return self.session.query(self.model).all()

    def update(self, obj_id: str, data: dict) -> Optional[T]:
        """update of an object"""
        try:
            obj = self.get(obj_id)
            if obj:
                for key, value in data.items():
                    if hasattr(obj, key):
                        setattr(obj, key, value)
                self.session.commit()
                return obj
            return None
        except Exception as e:
            self.session.rollback()
            raise e

    def delete(self, obj_id: str) -> bool:
        """deleting an objet"""
        try:
            obj = self.get(obj_id)
            if obj:
                self.session.delete(obj)
                self.session.commit()
                return True
            return False
        except Exception as e:
            self.session.rollback()
            raise e

    def get_by_attribute(self, attribute: str, value) -> Optional[T]:
        """Retrieves an object via a specific attribute"""
        return self.session.query(self.model).filter(
            getattr(self.model, attribute) == value
        ).first()
