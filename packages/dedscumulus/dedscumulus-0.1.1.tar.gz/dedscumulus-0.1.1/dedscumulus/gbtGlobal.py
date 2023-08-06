from greenbyteapi.greenbyteapi_client import GreenbyteapiClient

def createClient(CREDS,LOGGER):
    try:
        greenbyte_client = GreenbyteapiClient()
        greenbyte_client.config.x_api_key=CREDS['brz_token']
        greenbyte_client.config.customer=CREDS['brzConfig']
        return greenbyte_client
    except Exception as ge:
        LOGGER.warning(f"WARNING: Could not initiaze greenbyte_client: "+str(ge))
        return None

def getData(greenbyte_client,QUERY_PARAMS,LOGGER):
    tries=0
    while tries<3:
        try:
            return greenbyte_client.data.get_data(QUERY_PARAMS['deviceIds'],QUERY_PARAMS['signalIds'],QUERY_PARAMS['timestampStart'],QUERY_PARAMS['timestampFinish'],False,QUERY_PARAMS['resolution'],'device',0,None)
        except Exception as ge:
            tries+=1
            LOGGER.debug(f"WARNING: get_data from Breeze not received, try {tries}, devices: {QUERY_PARAMS['deviceIds']}, error: "+str(ge))
            if tries==3:
                if  "Read timed out" in str(ge):
                    LOGGER.warning(f"WARNING: get_data from Breeze timed out for devices: {QUERY_PARAMS['deviceIds']}. Full error: "+str(ge))
                else:
                    LOGGER.warning(f"WARNING: get_data from Breeze not received, devices: {QUERY_PARAMS['deviceIds']}, error: "+str(ge))
                return None
            
def getStatuses(greenbyte_client,QUERY_PARAMS,LOGGER):
    tries=0
    while tries<3:
        try:
            return greenbyte_client.statuses.get_statuses(QUERY_PARAMS['deviceIds'],QUERY_PARAMS['timestampStart'],QUERY_PARAMS['timestampFinish'],QUERY_PARAMS['categories'],
                                                          QUERY_PARAMS['lostProductionSignalId'],None,None,False,QUERY_PARAMS['pageSize'],QUERY_PARAMS['page'],False,'custom')
        except Exception as ge:
            tries+=1
            LOGGER.debug(f"WARNING: get_statuses from Breeze not received, try {tries}, devices: {QUERY_PARAMS['deviceIds']}, error: "+str(ge))
            if tries==3:
                if  "Read timed out" in str(ge):
                    LOGGER.warning(f"WARNING: get_statuses from Breeze timed out for devices: {QUERY_PARAMS['deviceIds']}. Full error: "+str(ge))
                else:
                    LOGGER.warning(f"WARNING: get_statuses from Breeze not received, devices: {QUERY_PARAMS['deviceIds']}, error: "+str(ge))
                return None
            
def getSites(greenbyte_client,QUERY_PARAMS,LOGGER):
    tries=0
    while tries<3:
        try:
            return greenbyte_client.assets.get_sites('siteId,metadata',QUERY_PARAMS['pageSize'],QUERY_PARAMS['page'])
        except Exception as ge:
            tries+=1
            LOGGER.debug(f"WARNING: get_sites from Breeze not received, try {tries}, error: "+str(ge))
            if tries==3:
                if  "Read timed out" in str(ge):
                    LOGGER.warning(f"WARNING: get_sites from Breeze timed out. Full error: "+str(ge))
                else:
                    LOGGER.warning(f"WARNING: get_sites from Breeze not received, error: "+str(ge))
                return None
            
def getDevices(greenbyte_client,QUERY_PARAMS,LOGGER):
    tries=0
    while tries<3:
        try:
            return greenbyte_client.assets.get_devices(QUERY_PARAMS['device_type_ids'],None,None,QUERY_PARAMS['fields'],QUERY_PARAMS['pageSize'],QUERY_PARAMS['page'],False)
        except Exception as ge:
            tries+=1
            LOGGER.debug(f"WARNING: get_devices from Breeze not received, try {tries}, error: "+str(ge))
            if tries==3:
                if  "Read timed out" in str(ge):
                    LOGGER.warning(f"WARNING: get_devices from Breeze timed out. Full error: "+str(ge))
                else:
                    LOGGER.warning(f"WARNING: get_devices from Breeze not received, error: "+str(ge))
                return None
            
def getTasks(greenbyte_client,QUERY_PARAMS,LOGGER):
    tries=0
    while tries<3:
        try:
            return greenbyte_client.plan.list_tasks(QUERY_PARAMS['timestampStart'],QUERY_PARAMS['timestampFinish'],
                        #device_ids=self.turbines,
                        site_ids=QUERY_PARAMS['sites'],
                        category_ids=QUERY_PARAMS['categoryIds'],
                        state=None,fields=None,page_size=QUERY_PARAMS['pageSize'],page=QUERY_PARAMS['page'],use_utc=False)
        except Exception as ge:
            tries+=1
            LOGGER.debug(f"WARNING: list_tasks from Breeze not received, try {tries}, error: "+str(ge))
            if tries==3:
                if  "Read timed out" in str(ge):
                    LOGGER.warning(f"WARNING: list_tasks from Breeze timed out. Full error: "+str(ge))
                else:
                    LOGGER.warning(f"WARNING: list_tasks from Breeze not received, error: "+str(ge))
                return None
            
def getTaskCategories(greenbyte_client,LOGGER):
    tries=0
    while tries<3:
        try:
            return greenbyte_client.plan.list_task_categories()
        except Exception as ge:
            tries+=1
            LOGGER.debug(f"WARNING: list_task_categories from Breeze not received, try {tries}, error: "+str(ge))
            if tries==3:
                if  "Read timed out" in str(ge):
                    LOGGER.warning(f"WARNING: list_task_categories from Breeze timed out. Full error: "+str(ge))
                else:
                    LOGGER.warning(f"WARNING: list_task_categories from Breeze not received, error: "+str(ge))
                return None