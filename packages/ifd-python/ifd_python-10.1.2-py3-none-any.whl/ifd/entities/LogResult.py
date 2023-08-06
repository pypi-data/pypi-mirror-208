from datetime import datetime

class LogResult():
    """Contient le log d'une analyse
    step : étape dans le workflow
    startTime : date de début de l'analyse
    stopTime : date de fin de l'analyse
    duration : durée de l'analyse
    result : le résultat de l'analyse; en cas d'erreur, contient le type d'erreur
    message : contient le message d'erreur en cas d'erreur
    """
    step : str = ""
    startTime : datetime = datetime(1753, 1, 1, 0, 0, 0)
    stopTime : datetime = datetime(1753, 1, 1, 0, 0, 0)
    duration : float = 0.0
    result : str = ""
    message : str = ""

    def serialize(self):
        return {
            "step": self.step,
            "startTime": self.startTime,
            "stopTime": self.stopTime,
            "duration": self.duration,
            "result": self.result,
            "message": self.message
        }
    def deserialize(self, data):
        for field in data:
            if field == "step":
                self.step = data[field]
            elif field == "startTime":
                self.startTime = data[field]
            elif field == "stopTime":
                self.stopTime = data[field]
            elif field == "duration":
                self.duration = data[field]
            elif field == "result":
                self.result = data[field]
            elif field == "message":
                self.message = data[field]
        return self
