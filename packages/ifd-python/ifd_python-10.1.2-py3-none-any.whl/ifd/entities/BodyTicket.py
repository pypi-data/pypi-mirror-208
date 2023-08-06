from .Malfacon import Malfacon
class BodyTicket:
    typeInfrastructure = "IMB"
    referencePBO = ""
    referencePTO = ""
    referencePM = ""
    refExploitation = ""
    malfacons = []

    def __dict__(self):
        return {
            "typeInfrastructure": self.typeInfrastructure,
            "referencePBO": self.referencePBO,
            "referencePTO": self.referencePTO,
            "referencePM": self.referencePM,
            "refExploitation": self.refExploitation,
            "malfacons": [m.__dict__() for m in self.malfacons] # Appel à la méthode spéciale __dict__ pour chaque instance de Malfacon
        }