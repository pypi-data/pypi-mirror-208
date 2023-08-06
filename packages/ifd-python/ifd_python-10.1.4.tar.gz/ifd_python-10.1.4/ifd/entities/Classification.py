from .Modele import Modele

class Classification():
    score: float = -1
    label: str = ""
    modele: Modele

    def serialize(self):
        return {
            "score": self.score,
            "label": self.label,
            "modele": self.modele.serialize() if isinstance(self.modele, Modele) else None
        }
    def deserialize(self, data):
        for field in data:
            if data[field] is None:
                pass
            elif field == "score":
                self.score = data[field]
            elif field == "label":
                self.label = data[field]
            elif field == "modele":
                self.modele = Modele().deserialize(data[field])
        return self