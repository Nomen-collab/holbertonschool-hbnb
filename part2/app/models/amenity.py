from app.models.base_model import BaseModel

class Amenity(BaseModel):
    def __init__(self, name):
        super().__init__()
        if len(name) > 50:
            raise ValueError("name must be 50 characters or less")
        self.name = name


    def to_dict(self):
        return {
            'id': self.id,  # ✅ Ajout des deux-points
            'name': self.name,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


    def update(self, data):
        """Function to update amenities attributes"""
        for key, value in data.items():
            if hasattr(self, key) and key != 'id':  # ✅ Parenthèse corrigée
                setattr(self, key, value)  # ✅ setattr + value en minuscule
        self.save()
