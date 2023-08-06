import requests
from urllib.parse import urljoin
import json
from datetime import datetime

class RestTicketRepository():
    
    token : str = ""
    expiration : str = ""
    
    uri : str = ""
    
    authRoute : str = ""
    user : str = ""
    password : str = ""
    sourceAPI : str = ""
    
    def __init__(self, uri, authRoute, user, password, sourceAPI):
        self.uri = uri
        self.authRoute = authRoute
        self.user = user
        self.password = password
        self.sourceAPI = sourceAPI
    
    def _getToken(self):
        url = urljoin(self.uri, self.authRoute)

        response = requests.post(
            url, 
            {
                "username": self.user, 
                "password": self.password,
                "sourceAPI": self.sourceAPI
            }
        )
        
        response.raise_for_status()
        
        content = json.loads(response.content.decode("utf-8"))

        self.token = content.get("token")
        self.expiration = datetime.fromtimestamp(content.get("expirationToken"))
    
    def _tokenIsValid(self):
        return (self.token != "" and self.expiration != "") and self.expiration > datetime.now()
           
    def postTicketMalfacon(self, route, ticket, img_bytes):
        if not self._tokenIsValid():
            self._getToken()
            
        url = urljoin(self.uri, route)
        malfacon = json.loads(ticket.ita_ticket_request)["malfacons"]
        
        files = {}
        
        for m in malfacon :
            files.update(
                {
                    "fichiers[{codeConversion}][{idX3}]".format(
                        codeConversion=m["codeConversion"], 
                        idX3=m["idX3"]
                        )
                    : img_bytes
                }
            )
            
        response = requests.post(
            url,
            headers={'Authorization': "Bearer {}".format(self.token)},
            params={
                'ticket' : ticket.ita_ticket_request,
                'libelleReferentielSource': self.sourceAPI
                },
            files=files         
        )
        
        return response.status_code, response.text, response.ok