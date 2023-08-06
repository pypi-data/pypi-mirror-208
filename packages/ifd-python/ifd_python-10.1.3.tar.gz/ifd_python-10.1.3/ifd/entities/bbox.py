class bbox():
    xmin: float
    xmax: float
    ymin: float
    ymax: float

    def serialize(self):
        return {
            "xmin": self.xmin,
            "xmax": self.xmax,
            "ymin": self.ymin,
            "ymax": self.ymax
        }
    def deserialize(self, data):
        for field in data:
            if data[field] is None:
                pass
            elif field == "xmin":
                self.xmin = data[field]
            elif field == "xmax":
                self.xmax = data[field]
            elif field == "ymin":
                self.ymin = data[field]
            elif field == "ymax":
                self.ymax = data[field]
        return self
    