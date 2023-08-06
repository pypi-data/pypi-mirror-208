import time
import requests
import pyodbc
import json

SYSTEMSHORTNAME='brz'

def getDataSignals(CREDS, logger):
    try:
        allDataSignals={}
        brzUrlDatasignals=getSetting(CREDS, 1, 'brzUrlDatasignals',logger)
        prms = {'apiToken': CREDS['brz_token']}
        hdrs={'Content-Type': 'application/json'}
        r = requests.get(brzUrlDatasignals, headers=hdrs, params=prms)
        allDataSignals=json.loads(r.text)
        if len(allDataSignals)>0:
            return allDataSignals
        log_text="brzGlobal2.getDataSignals returned zero results"
        logger.warning(f"WARNING: {log_text}")
        return None
    except Exception as e1:
        log_text="brzGlobal2.getDataSignals Failed, error: "+str(e1)
        logger.error(f"ERROR: {log_text}")
        return None

def getSetting(CREDS, version, settingName, logger):
    try:
        with pyodbc.connect(f"Driver={CREDS['driver']};Server=tcp:{CREDS['db_server']},1433;Database={CREDS['database']};Uid={CREDS['db_user']};Pwd="+"{"+CREDS['db_password']+"};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30") as conn:
            with conn.cursor() as cursor:
                sql_select=f"DECLARE @systemid INT=(SELECT [SystemId] FROM [dbo].[mstSystems] WHERE [Name]='Breeze'); SELECT [setting] FROM [dbo].[mstSettings] WHERE [settingVersion]={version} AND [settingName]='{settingName}' AND [SystemId]=@systemid;"
                logger.debug(f"Running SQL: {sql_select}")
                cursor.execute(sql_select)
                result=cursor.fetchone()[0]
                logger.debug(f"brzGlobal2.getSetting returned {result}")
                return result
    except Exception as e1:
        log_text="brzGlobal2.getSetting Failed, error: "+str(e1)
        logger.error(f"ERROR: {log_text}")
        return None

def getAssetIds(CREDS, logger):
    try:
        assetIds={}
        conn_string='Driver='+CREDS['driver']+';Server=tcp:'+CREDS['db_server']+',1433;Database='+CREDS['database']+';Uid='+CREDS['db_user']+';Pwd={'+CREDS['db_password']+'};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30'
        logger.debug(f"Connection: {conn_string}")
        with pyodbc.connect(conn_string) as conn:
            with conn.cursor() as cursor:
                cursor.execute("DECLARE @turbineid INT=(SELECT [AssetTypeId] FROM [dbo].[mstAssetType] WHERE [Name]='Turbine'); SELECT [AssetId],JSON_VALUE([SystemIds], '$.brz') AS [brzId],JSON_VALUE([Info], '$.ratedPower') AS [RatedPower] FROM [dbo].[mstAssets] WHERE [AssetTypeId]=@turbineid AND JSON_VALUE([SystemIds], '$.brz') IS NOT NULL")
                for row in cursor:
                    item={}
                    item['AssetId']=row[0]
                    item['RatedPower']=row[2]
                    assetIds[row[1]]=item
        if len(assetIds)>0:
            return assetIds
        log_text="brzGlobal2.getAssetIds returned zero results"
        logger.warning(f"WARNING: {log_text}")
        return None
    except Exception as e1:
        log_text="brzGlobal2.getAssetIds Failed, error: "+str(e1)
        logger.error(f"ERROR: {log_text}")
        return None

def getAssetPerSiteIds(CREDS, siteIds, logger):
    try:
        assetIds={}
        with pyodbc.connect('Driver='+CREDS['driver']+';Server=tcp:'+CREDS['db_server']+',1433;Database='+CREDS['database']+';Uid='+CREDS['db_user']+';Pwd={'+CREDS['db_password']+'};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30') as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"DECLARE @turbineid INT=(SELECT [AssetTypeId] FROM [dbo].[mstAssetType] WHERE [Name]='Turbine'); DECLARE @siteid INT=(SELECT [AssetTypeId] FROM [dbo].[mstAssetType] WHERE [Name]='Site'); SELECT [AssetId],JSON_VALUE([SystemIds], '$.brz') AS [brzId] FROM [dbo].[mstAssets] WHERE [AssetTypeId]=@turbineid AND [SiteId] IN (SELECT [AssetId] FROM [dbo].[mstAssets] WHERE [AssetTypeId]=@siteid and (JSON_VALUE([SystemIds], '$.brz') in ({siteIds}))) AND JSON_VALUE([SystemIds], '$.brz') IS NOT NULL;")
                for row in cursor:
                    item={}
                    item['AssetId']=row[0]
                    assetIds[row[1]]=item
        if len(assetIds)>0:
            return assetIds
        log_text="brzGlobal2.getAssetPerSiteIds returned zero results"
        logger.warning(f"WARNING: {log_text}")
        return None
    except Exception as e1:
        log_text="brzGlobal2.getAssetPerSiteIds Failed, error: "+str(e1)
        logger.error(f"ERROR: {log_text}")
        return None

def getPowerCurve(CREDS, assetId, logger):
    try:
        errors=0
        while errors<3:
            try:
                powerCurve={}
                with pyodbc.connect('Driver='+CREDS['driver']+';Server=tcp:'+CREDS['db_server']+',1433;Database='+CREDS['database']+';Uid='+CREDS['db_user']+';Pwd={'+CREDS['db_password']+'};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30') as conn:
                    with conn.cursor() as cursor:
                        cursor.execute("SELECT [windSpeed],[power] FROM [dbo].[brzPowerCurve] WHERE [AssetId]="+str(assetId))
                        for row in cursor:
                            powerCurve[row[0]]=row[1]
                return powerCurve
            except pyodbc.Error as pe:
                log_text="brzGlobal2.getPowerCurve Failed ("+str(errors)+"), error code: "+str(pe.args[0])+", retrying. Error text: "+str(pe)#to be removed after I see it work
                logger.warning(f"WARNING: {log_text}")
                errors+=1
                time.sleep(50)
        log_text="brzGlobal2.getPowerCurve Failed 3 times, stopping execution"
        logger.error(f"ERROR: {log_text}")
        return None
    except Exception as e1:
        log_text="brzGlobal2.getPowerCurve Failed, error: "+str(e1)
        logger.error(f"ERROR: {log_text}")
        return None

def getPowerCurves(CREDS, logger):
    try:
        errors=0
        while errors<3:
            try:
                powerCurves={}
                with pyodbc.connect('Driver='+CREDS['driver']+';Server=tcp:'+CREDS['db_server']+',1433;Database='+CREDS['database']+';Uid='+CREDS['db_user']+';Pwd={'+CREDS['db_password']+'};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30') as conn:
                    with conn.cursor() as cursor:
                        cursor.execute("SELECT [AssetId],[windSpeed],[power] FROM [dbo].[brzPowerCurve]")
                        for row in cursor:
                            try:
                                powerCurves[row[0]][row[1]]=row[2]
                            except:
                                powerCurves[row[0]]={}
                                powerCurves[row[0]][row[1]]=row[2]
                return powerCurves
            except pyodbc.Error as pe:
                log_text="brzGlobal2.getPowerCurves Failed ("+str(errors)+"), error code: "+str(pe.args[0])+", retrying. Error text: "+str(pe)#to be removed after I see it work
                logger.warning(f"WARNING: {log_text}")
                errors+=1
                time.sleep(50)
        log_text="brzGlobal2.getPowerCurves Failed 3 times, stopping execution"
        logger.error(f"ERROR: {log_text}")
        return None
    except Exception as e1:
        log_text="brzGlobal2.getPowerCurves Failed, error: "+str(e1)
        logger.error(f"ERROR: {log_text}")
        return None

def getTurbinesInfo(CREDS, logger):
    try:
        mstTurbinesInfo={}
        with pyodbc.connect('Driver='+CREDS['driver']+';Server=tcp:'+CREDS['db_server']+',1433;Database='+CREDS['database']+';Uid='+CREDS['db_user']+';Pwd={'+CREDS['db_password']+'};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30') as conn:
            with conn.cursor() as cursor:
                cursor.execute("DECLARE @turbineid INT=(SELECT [AssetTypeId] FROM [dbo].[mstAssetType] WHERE [Name]='Turbine'); SELECT JSON_VALUE([SystemIds],'$.brz'),[Coordinates],[Info] FROM [dbo].[mstAssets] WHERE [AssetTypeId]=@turbineid AND [SystemIds] IS NOT NULL AND [Info] IS NOT NULL AND [Coordinates] IS NOT NULL;")
                for row in cursor:
                    mstTurbinesInfo[row[0]]={}
                    mstTurbinesInfo[row[0]]['Coordinates']=row[1]
                    mstTurbinesInfo[row[0]]['Info']=row[2]
        if len(mstTurbinesInfo)>0:
            return mstTurbinesInfo
        log_text="brzGlobal2.getTurbinesInfo returned zero results"
        logger.warning(f"WARNING: {log_text}")
        return None
    except Exception as e1:
        log_text="brzGlobal2.getTurbinesInfo Failed, error: "+str(e1)
        logger.error(f"ERROR: {log_text}")
        return None
