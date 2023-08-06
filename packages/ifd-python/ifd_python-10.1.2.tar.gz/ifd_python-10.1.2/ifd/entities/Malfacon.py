class Malfacon:
    codeConversion = ""
    quantite = 1
    commentaire = ""
    isDangerImmediat = False
    isIncludePhotoReprise = False
    commentaireReprise = ""
    idX3 = ""
    referenceInterne = ""
    isNonImputable = False
    
    def __dict__(self):
        return {
            "codeConversion": self.codeConversion,
            "quantite": self.quantite,
            "commentaire": self.commentaire,
            "isDangerImmediat": self.isDangerImmediat,
            "isIncludePhotoReprise": self.isIncludePhotoReprise,
            "commentaireReprise": self.commentaireReprise,
            "idX3": self.idX3,
            "referenceInterne": self.referenceInterne,
            "isNonImputable": self.isNonImputable
        }