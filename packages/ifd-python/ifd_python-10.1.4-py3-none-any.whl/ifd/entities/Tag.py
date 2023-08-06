from .Modele import Modele

class Tag():
    score: float = -1
    label: str = ""
    description: str = ""
    modele: Modele = None
    isMalfacon: bool = False

    def serialize(self):
        return {
            "score": self.score,
            "label": self.label,
            "description": self.description,
            "modele": self.modele.serialize() if isinstance(self.modele, Modele) else None,
            "isMalfacon": self.isMalfacon
        }
    def deserialize(self, data):
        for field in data:
            if data[field] is None:
                pass
            elif field == "score":
                self.score = data[field]
            elif field == "label":
                self.label = data[field]
            elif field == "description":
                self.description = data[field]
            elif field == "modele":
                self.modele = Modele().deserialize(data[field])
            elif field == "isMalfacon":
                self.isMalfacon = data[field]
        return self
        