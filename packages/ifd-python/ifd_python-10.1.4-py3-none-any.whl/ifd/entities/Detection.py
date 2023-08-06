from .bbox import bbox
from .Modele import Modele
from .Couleur import Couleur
from .Abstract import ADetection

class Detection(ADetection):
    couleurs : list = []

    def serialize(self):
        data = super().serialize()
        data["couleurs"] = [couleur.serialize() if isinstance(couleur, Couleur) else None for couleur in self.couleurs]
        return data
    
    def deserialize(self, data):
        super().deserialize(data)
        for field in data:
            if data[field] is None:
                pass
            elif field == "couleurs":
                self.couleurs = [Couleur().deserialize(element) for element in data[field]]
        return self
    
    
