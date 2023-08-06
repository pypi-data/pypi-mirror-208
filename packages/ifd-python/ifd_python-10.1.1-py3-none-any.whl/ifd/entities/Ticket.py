class Ticket():
    ita_id : int = None
    img_id : int = None
    ita_ticket_request : str = None
    ita_validation_statut : str = None
    iva_id : int = None
    ita_date_action : str = None
    ita_date_creation : str = None
    ita_user_action : str = None
    ita_motif_rejet : str = None
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key.lower(), value)