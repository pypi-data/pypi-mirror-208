class Modele():
    label: str
    version: str
    def serialize(self):
        return {
            "label": self.label,
            "version": self.version
        }
    def deserialize(self, data):
        for field in data:
            if data[field] is None:
                pass
            elif field == "label":
                self.label = data[field]
            elif field == "version":
                self.version = data[field]
        return self