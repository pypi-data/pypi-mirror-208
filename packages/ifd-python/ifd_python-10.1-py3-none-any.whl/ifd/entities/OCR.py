from .Abstract import ADetection

class OCR(ADetection):
    score : float = 0.0
    label_ocr: str = ''
    score_match: float = 0.0

    def serialize(self):
        data = super().serialize()
        data["score"] = self.score
        data["label_ocr"] = self.label_ocr
        data["score_match"] = self.score_match
        return data
        
    def deserialize(self, data):
        super().deserialize(data)

        for field in data:
            if data[field] is None:
                pass
            elif field == "label_ocr":
                self.label_ocr = data[field]
            elif field == "score_match":
                self.score_match = data[field]
            elif field == "score":
                self.score = data[field]
        return self