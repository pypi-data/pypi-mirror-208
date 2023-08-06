class Intervention :
    def __init__(self, id="", refOC="", refPM="", refPBO="", refPTO="", refIMB = "", photos=[]):
        self.id = id
        self.refOC = refOC
        self.photos = photos
        self.refPM = refPM
        self.refPBO = refPBO
        self.refPTO = refPTO
        self.refIMB = refIMB
    
    def __str__(self):
        return "Intervention : " + str(self.id) + " " + str(self.refOC) + " " + str(self.refPM) + " " + str(self.refPBO) + " " + str(self.refPTO) + " " + str(self.refIMB) + " " + str(self.photos)
    def __dict__(self):
        return {"id": self.id, "refOC": self.refOC, "refPM": self.refPM, "refPBO": self.refPBO, "refPTO": self.refPTO, "refIMB":self.refIMB, "photos": self.photos}
    
    