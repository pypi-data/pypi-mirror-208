import time
from datetime import datetime
import pyodbc
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from azure.keyvault.secrets import SecretClient
from azure.identity import ManagedIdentityCredential
from sqlalchemy import create_engine
import urllib

def getAssetTypes(DB_CRED,logger):
    current_row=''
    assetTypes={}
    try:
        logger.debug("Starting getAssetTypes")
        errors=0
        while errors<3:
            try:
                with pyodbc.connect('Driver='+DB_CRED['driver']+';Server=tcp:'+DB_CRED['db_server']+',1433;Database='+DB_CRED['database']+';Uid='+DB_CRED['db_user']+';Pwd={'+DB_CRED['db_password']+'};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30') as conn:
                    with conn.cursor() as cursor:
                        cursor.execute("SELECT [AssetTypeId],[ExternalName] FROM [dbo].[mstAssetType] WHERE [ExternalName] IS NOT NULL;")
                        for row in cursor:
                            current_row=str(row)
                            assetTypes[row[1]]=row[0]
                        return assetTypes
            except Exception as pe:
                errors+=1
                time.sleep(0.05)
        log_text="mstAst.getAssetTypes Failed 3 times, stopping execution"
        logger.error(log_text)
        return None
    except Exception as e1:
        log_text=f"mstAst.getAssetTypes Failed, error: {e1}, current_row: {current_row}"
        logger.error(log_text)
        return None

def getBrzAssetIds(DB_CRED,LOGGER):
    assetIds={}
    try:
        with pyodbc.connect('Driver='+DB_CRED['driver']+';Server=tcp:'+DB_CRED['db_server']+',1433;Database='+DB_CRED['database']+';Uid='+DB_CRED['db_user']+';Pwd={'+DB_CRED['db_password']+'};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30') as conn:
            with conn.cursor() as cursor:
                cursor.execute("DECLARE @turbineid INT=(SELECT [AssetTypeId] FROM [dbo].[mstAssetType] WHERE [Name]='Turbine');SELECT [AssetId],JSON_VALUE([SystemIds], '$.brz') AS [brzId],JSON_VALUE([Info], '$.ratedPower') AS [RatedPower] FROM [dbo].[mstAssets] WHERE [AssetTypeId]=@turbineid AND JSON_VALUE([SystemIds], '$.brz') IS NOT NULL;")
                for row in cursor:
                    item={}
                    item['AssetId']=row[0]
                    item['RatedPower']=row[2]
                    assetIds[row[1]]=item
        if len(assetIds)>0:
            return assetIds
        log_text="mstAst.getBrzAssetIds returned zero results"
        LOGGER.warning(log_text)
        return None
    except Exception as e1:
        log_text="mstAst.getBrzAssetIds Failed, error: "+str(e1)
        LOGGER.error(log_text)
        return None
    
def executeCommand(DB_CRED,sql,logger):
    #this function returns negatie values in case of an error!!!
    try:
        #logger.debug(f"mstAst.executeCommand / Executing an SQL command")
        errors=0
        while errors<3:
            try:
                with pyodbc.connect('Driver='+DB_CRED['driver']+';Server=tcp:'+DB_CRED['db_server']+',1433;Database='+DB_CRED['database']+';Uid='+DB_CRED['db_user']+';Pwd={'+DB_CRED['db_password']+'};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30') as conn:
                    with conn.cursor() as cursor:
                        logger.debug(f"mstAst.executeCommand / sql: {sql[:5000]}")
                        cursor.execute(sql)
                        rows=int("{}".format(cursor.rowcount))
                        logger.debug(f"mstAst.executeCommand / Received {rows} rows from cursor")
                        if rows==0:
                            #logger.debug(f"mstAst.executeCommand / 0 rows from cursor, returning 1")
                            return 1#so that we know that execution was successful
                        return rows
            except Exception as s1:
                if errors==0:
                    logger.warning(f"mstAst.executeCommand / first failure: "+str(s1)[:5000]+", command: "+str(sql[:2500]))
                if "Violation of UNIQUE KEY constraint" in s1.args[1]:
                    logger.warning(f"mstAst.executeCommand / Violation of UNIQUE KEY constraint detected")
                    return -2
                if "The number of row value expressions in the INSERT statement exceeds the maximum allowed number of 1000" in s1.args[1]:
                    logger.warning(f"mstAst.executeCommand / INSERT statement exceeds the maximum allowed number of 1000")
                    return -3
                errors+=1
                time.sleep(0.05)
        logger.error("mstAst.executeCommand Failed 3 times, stopping execution, last command: "+str(sql[:2500]))
        return -1
    except Exception as e1:
        logger.error(f"mstAst.executeCommand Failed, error: {e1.args[1]}, sql: {sql[:2500]}")
        return -1
        
def executeSelect(DB_CRED,sql,logger):
    selectRows=[]
    try:
        logger.debug(f"mstAst.executeSelect / Executing {sql}")
        errors=0
        error_text=None
        while errors<3:
            try:
                with pyodbc.connect('Driver='+DB_CRED['driver']+';Server=tcp:'+DB_CRED['db_server']+',1433;Database='+DB_CRED['database']+';Uid='+DB_CRED['db_user']+';Pwd={'+DB_CRED['db_password']+'};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30') as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(sql)
                        for row in cursor:
                            selectRows.append(row)
                        return selectRows
            except Exception as pe:
                error_text=str(pe)
                errors+=1
                time.sleep(0.05)
        log_text="mstAst.executeSelect Failed 3 times, stopping execution"
        if error_text is not None:
            log_text+=f". Last thrown error: {error_text}"
        logger.error(log_text)
        return None
    except Exception as e1:
        log_text=f"mstAst.executeSelect Failed, error: "+str(e1)[:1000]
        logger.error(log_text)
        return selectRows
        
def getAssetParameter(DB_CRED,assetId,parameter,logger,subParameter=None):
    try:
        logger.debug("Starting getAssetParameter")
        errors=0
        while errors<3:
            try:
                if subParameter is None:
                    sql=f"SELECT [{parameter}] FROM [dbo].[mstAssets] WHERE [AssetId]={assetId};"
                else:
                    sql=f"SELECT JSON_VALUE([{parameter}],'$.{subParameter}') FROM [dbo].[mstAssets] WHERE [AssetId]={assetId};"
                #assetTypes={}
                with pyodbc.connect('Driver='+DB_CRED['driver']+';Server=tcp:'+DB_CRED['db_server']+',1433;Database='+DB_CRED['database']+';Uid='+DB_CRED['db_user']+';Pwd={'+DB_CRED['db_password']+'};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30') as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(sql)
                        for row in cursor:
                            return row[0]
                        return None#if no rows are returned, return none
            except:
                errors+=1
                time.sleep(0.05)
        log_text=f"mstAst.getAssetParameter Failed 3 times, stopping execution"
    except Exception as e1:
        log_text=f"mstAst.getAssetParameter Failed, error: {e1:[:1000]}"
        logger.error(log_text)
        
def getColumnEntry(DB_CRED,getWhat,tableFrom,whereFilter,equalsWhat,string,logger):
    try:
        logger.debug(f"mstAst.getColumnEntry / Getting {getWhat} from {tableFrom} on {DB_CRED['db_server']}.{DB_CRED['database']}")
        errors=0
        exc_text=""
        while errors<3:
            try:
                if string==1:
                    sql="SELECT "+getWhat+" FROM [dbo].["+tableFrom+"] WHERE ["+whereFilter+"]='"+equalsWhat+"';"
                else:
                    sql="SELECT "+getWhat+" FROM [dbo].["+tableFrom+"] WHERE ["+whereFilter+"]="+str(equalsWhat)+";"
                logger.debug(f"mstAst.getColumnEntry / SQL: {sql}")
                #print(sql)
                with pyodbc.connect('Driver='+DB_CRED['driver']+';Server=tcp:'+DB_CRED['db_server']+',1433;Database='+DB_CRED['database']+';Uid='+DB_CRED['db_user']+';Pwd={'+DB_CRED['db_password']+'};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30') as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(sql)
                        for row in cursor:
                            logger.debug(f"mstAst.getColumnEntry OK, result: {row[0]}")
                            return row[0]
                        return None#if no rows are returned, return none
            except Exception as e2:
                log_text=f"mstAst.getColumnEntry Failed, error2: {e2}"
                exc_text=str(e2)[:500]
                errors+=1
                time.sleep(0.05)
        log_text=f"mstAst.getColumnEntry Failed 3 times, stopping execution, error: {exc_text}"
        return None
    except Exception as e1:
        log_text=f"mstAst.getColumnEntry Failed, error1: {e1}"
        logger.error(log_text)
        return None

def buildMimeMessage(sender, subject, text, to_address, prio, text_type,cc_address,bcc_address):
    msg = MIMEMultipart('html')
    msg['From'] = sender
    msg['To'] = to_address
    msg['Cc'] = cc_address
    msg['Bcc'] = bcc_address
    msg['Subject'] = subject
    body = text
    msg['X-Priority'] = prio
    msg.attach(MIMEText(body, text_type))
    return msg
    
def sendEmail(CREDS, subject, text, to_address, prio, text_type, logger, cc_address=None, bcc_address=None):
    try:
        #text_type: 'html'
        logger.debug("Starting sendEmail")
        message = buildMimeMessage(CREDS["email_username"], subject, text, to_address, str(prio), text_type, cc_address, bcc_address)
        exch=smtplib.SMTP(CREDS["email_server"], CREDS["email_port"])
        exch.starttls()
        exch.login(CREDS["email_username"], CREDS["email_password"])
        exch.send_message(message)
        exch.quit()
        return 0
    except Exception as e1:
        log_text=f"mstAst.sendEmail Failed, error: "+str(e1)[:1000]
        logger.error(log_text)
        return -1
        
def getSetting(CREDS,version,settingName,systemShortName,logger):
    #this version of the function is using one mstSettings table instead of multiple ones like in the past
    try:
        logger.debug("Starting getSetting")
        errors=0
        while errors<3:
            try:
                sql=f"DECLARE @sysid INT=(SELECT [systemId] from [mstSystems] WHERE [shortName]='{systemShortName}');SELECT [Setting] FROM [dbo].[mstSettings] WHERE [settingVersion]={version} AND [settingName]='{settingName}' and [systemId]=@sysid;"
                logger.debug(f"SQL: {sql}")
                conn_string='Driver='+CREDS['driver']+';Server=tcp:'+CREDS['db_server']+',1433;Database='+CREDS['database']+';Uid='+CREDS['db_user']+';Pwd={'+CREDS['db_password']+'};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30'
                logger.debug(f"Connection: {conn_string}")
                with pyodbc.connect(conn_string) as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(sql)
                        return cursor.fetchone()[0]
            except Exception as pe:
                logger.error(f"Failed getting setting: {pe}")
                errors+=1
                time.sleep(0.05)
        log_text=f"mstAst.getSetting Failed 3 times, stopping execution"
        logger.error(log_text)
        return None
    except Exception as e1:
        log_text=f"mstAst.getSetting Failed, error: "+str(e1)[:1000]
        logger.error(log_text)
        return None
        
def dfToDB2(CREDS,table,df,chunkSize,logger):
    try:
        #logger.debug(f"Starting mstAst4.dfToDB to table {table}")
        #logger.debug(f"Creating connection")
        conn_str=urllib.parse.quote_plus(r'Driver='+CREDS['driver']+';Server=tcp:'+CREDS['db_server']+',1433;Database='+CREDS['database']+';Uid='+CREDS['db_user']+';Pwd='+CREDS['db_password']+';Encrypt=yes;TrustServerCertificate=yes;Connection Timeout=30;')
        conn='mssql+pyodbc:///?odbc_connect={}'.format(conn_str)
        engine=create_engine(conn, fast_executemany=True, echo=False)
        #engine=create_engine(conn, fast_executemany=False, echo=False)
        #logger.debug(f"Executing df.to_sql")
        #result=df.to_sql(table, engine, if_exists='append', chunksize=chunkSize, index=False, method='multi')
        logger.debug(f"dfToDB2 executing")
        timestampStart = datetime.now()
        result=df.to_sql(table, engine, if_exists='append', chunksize=chunkSize, index=False)
        timestampEnd=datetime.now()
        runTime=str(timestampEnd-timestampStart)[:-7]
        size=len(df.index)
        logger.debug(f"mstAst.dfToDB2 storing to table {table} ended with chunksize: {chunkSize}, result: {result}, size: {size} in {runTime}")

        if isinstance(result, int) or result is None:
            return 0
        else:
            logger.warning(f"mstAst.dfToDB2 storing to table {table} ended with result: {result}, size: {size}, returning 0")
        if size>chunkSize:
            logger.debug(f"mstAst.dfToDB2 storing to table {table} ended with result: {result}, size: {size}, returning 0")
        return 0
    except Exception as e1:
        log_text=f"mstAst.dfToDB2, storing to table {table} failed, error: "+str(e1)[:5000]
        logger.error(log_text)
        #logger.error(e1)
        #raise
        #raise error.with_traceback(sys.exc_info()[2])
        return 1
        
def getVaultSecret(CREDS,vaultName,secretName,logger):
    try:
        logger.debug("Starting getVaultSecret")
        #keyVaultName = "dv-kv-monsys"
        #secretName="dv-sql"
        KVUri = f"https://{vaultName}.vault.azure.net"
        #credential = DefaultAzureCredential()
        credential = ManagedIdentityCredential(client_id="031ce06f-fd5a-41a4-a62c-8ad477e71e98")
        client = SecretClient(vault_url=KVUri, credential=credential)
        secret = client.get_secret(secretName)
        return secret.value
    except Exception as e1:
        log_text=f"mstAst.getVaultSecret Failed, error: {e1}[:500]"
        logger.error(log_text)
        return None
