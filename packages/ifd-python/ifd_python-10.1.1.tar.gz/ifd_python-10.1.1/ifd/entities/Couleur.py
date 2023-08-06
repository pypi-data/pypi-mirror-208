from .Abstract import ADetection

class Couleur(ADetection):
    
    def serialize(self):
        return super().serialize()
    
    def deserialize(self, data):
        super().deserialize(data)
        return self
