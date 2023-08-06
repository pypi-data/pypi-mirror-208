from pymssql import connect, Connection

class AbsSqlRepository():
    
    connection : Connection = None
    
    db_name = None
    db_host = None
    db_password = None
    db_user = None
    
    is_open = False
    
    def __init__(self, db_name, db_host, db_password, db_user):
        
        self.db_name = db_name
        self.db_host = db_host
        self.db_password = db_password
        self.db_user = db_user
        
        self._connectToDatabase()
        
    def _connectToDatabase(self):
        self.connection = connect(
            server=self.db_host, 
            user=self.db_user,
            password=self.db_password,
            database=self.db_name
            )
        is_open = True
        
    def commit(self):
        self.connection.commit()
        
    def rollback(self):
        self.connection.rollback()
        
    def close(self):
        is_open = False
        self.connection.close()