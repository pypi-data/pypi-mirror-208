from .Classification import Classification
from .Detection import Detection
from .Tag import Tag
from .OCR import OCR

class Image():
    id: int = -1
    img_path : str = ""
    img_checksum: str = ""
    classification: Classification = None
    detections: list = []
    tags: list = []
    rotation: int = 0
    ocr : OCR = None
    is_blur : bool = False
    
    ref_infra_pto : str = ""

    def serialize(self):
        return {
            "id": self.id,
            "img_path": self.img_path,
            "img_checksum": self.img_checksum,
            "rotation": self.rotation,
            "classification": self.classification.serialize() if isinstance(self.classification, Classification) else None,
            "tags": [tag.serialize() if isinstance(tag, Tag) else None for tag in self.tags],
            "detections": [detection.serialize() if isinstance(detection, Detection) else None for detection in self.detections],
            "ocr": self.ocr.serialize() if isinstance(self.ocr,OCR) else None,
            "ref_infra_pto": self.ref_infra_pto,
            "is_blur": self.is_blur
        }
    def deserialize(self, data):
        
        for field in data:
            print(field)
            if data[field] is None:
                pass
            elif field == "id":
                self.id = data[field]
            elif field == "img_path":
                self.img_path = data[field]
            elif field == "img_checksum":
                self.img_checksum = data[field]
            elif field == "classification":
                self.classification = Classification().deserialize(data[field])
            elif field == "rotation":
                self.rotation = data[field]
            elif field == "tags":
                self.tags = [Tag().deserialize(element) for element in data[field]]
            elif field == "detections":
                self.detections = [Detection().deserialize(element) for element in data[field]]
            elif field == "ocr":
                self.ocr = OCR().deserialize(data[field])
            elif field == "ref_infra_pto":
                self.ref_infra_pto = data[field]
            elif field == "is_blur":
                self.is_blur = data[field]
        return self