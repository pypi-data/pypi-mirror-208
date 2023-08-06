import logging
from .TableLogHandler import TableLogHandler

class Log:
    def __init__(self, CREDS, log_table, log_level):
        #logger.setLevel(logging.DEBUG)
        #notset=0
        #trace=5\does not exist!
        #debug=10
        #info=20
        #warning=30
        #error=40
        #critical=50
        
        self.logger = logging.getLogger('azure-storage')
        self.logger.setLevel(int(log_level))
        if len(self.logger.handlers)>0:
            self.logger.handlers.clear()
        self.azure_blob_handler = TableLogHandler(account_name=CREDS["mystorageaccountname"],
                                            account_key=CREDS["mystorageaccountkey"],
                                            table_name=log_table)
        self.logger.addHandler(self.azure_blob_handler)