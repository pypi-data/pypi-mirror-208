from .abstract import AbsSqlRepository
import pandas as pd 
from ..entities import Ticket

class SqlTicketRepository(AbsSqlRepository):
    
    def getAll(self):
        if not self.is_open:
            self._connectToDatabase()
            
        df = pd.read_sql(
            """
            SELECT [ITA_ID]
                ,[IMG_ID]
                ,[ITA_TICKET_REQUEST]
                ,[ITA_VALIDATION_STATUT]
                ,[IVA_ID]
                ,[ITA_DATE_ACTION]
                ,[ITA_DATE_CREATION]
                ,[ITA_USER_ACTION]
                ,[ITA_MOTIF_REJET]
            FROM [Infradeep].[dbo].[T_D_IRRIS_TICKET_AUTOMATIC_ITA]
            WHERE ITA_VALIDATION_STATUT = 'RETRY_CREATION_READY' OR ITA_VALIDATION_STATUT = 'ATT_VALIDATION'
            """, 
            self.connection
        )
        
        return self._dataframe_to_list_of_ticket(df)
    
    def updateStatut(self, ticket, statut):
        if not self.is_open:
            self._connectToDatabase()
            
        cur = self.connection.cursor()
        req = f"""
            UPDATE [Infradeep].[dbo].[T_D_IRRIS_TICKET_AUTOMATIC_ITA]
            SET ITA_VALIDATION_STATUT = '{statut}'
            WHERE ITA_ID = {ticket.ita_id}
            """
        cur.execute(req)
        cur.close()
        
    def insertLog(self, ticket, sendRoute, response, expediteur):
        if not self.is_open:
            self._connectToDatabase()
            
        cur = self.connection.cursor()
        req = f"""
            INSERT INTO T_L_LOGS_IRRIS_LIR (IMG_ID ,LIR_ROUTE ,LIR_REQUEST ,LIR_RESPONSE ,LIR_EXPEDITEUR)
            VALUES(
            {ticket.img_id},
            '{sendRoute}',
            '{ticket.ita_ticket_request}',
            '{response}',
            '{expediteur}'
            )
            """
        cur.execute(req)
        cur.close()
                
        
    def _dataframe_to_list_of_ticket(self, df):
        return [Ticket(**kwargs) for kwargs in df.to_dict(orient='records')]