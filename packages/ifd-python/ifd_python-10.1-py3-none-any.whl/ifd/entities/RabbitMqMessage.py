from Image import Image
from LogResult import LogResult

class RabbitMqMessage:
    """Contient le message envoyé au travers de RabbitMQ"""
    def __init__(self, log: LogResult, image: Image):
        self.log = log
        self.image = image
    
    def serialize(self):
        return {
            'log': self.log.serialize(),
            'image': self.image.serialize()
        }
    
    def deserialize(self, data):
        self.log.deserialize(data['log'])
        self.image.deserialize(data['image'])