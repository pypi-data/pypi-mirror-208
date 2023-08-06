from abc import ABC, abstractmethod
from ..bbox import bbox
from ..Modele import Modele

class ADetection(ABC):
    score: float
    label: str
    bbox: bbox
    modele: Modele

    @abstractmethod
    def serialize(self):
        return {
            "score": self.score,
            "label": self.label,
            "bbox": self.bbox.serialize() if isinstance(self.bbox, bbox) else None,
            "modele": self.modele.serialize() if isinstance(self.modele, Modele) else None,
        }
    
    @abstractmethod
    def deserialize(self, data):
        for field in data:
            if field == "score":
                self.score = data[field]
            elif field == "label":
                self.label = data[field]
            elif field == "bbox":
                self.bbox = bbox().deserialize(data[field])
            elif field == "modele":
                self.modele = Modele().deserialize(data[field])
        return self