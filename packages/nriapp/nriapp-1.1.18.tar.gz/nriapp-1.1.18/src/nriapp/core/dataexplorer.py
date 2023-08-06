from azure.kusto.data import KustoConnectionStringBuilder, DataFormat
from azure.kusto.ingest import QueuedIngestClient, IngestionProperties, FileDescriptor, BlobDescriptor
from datetime import timedelta

from azure.kusto.data import KustoClient, KustoConnectionStringBuilder, ClientRequestProperties
from azure.kusto.data.exceptions import KustoServiceError
from azure.kusto.data.helpers import dataframe_from_result_table
from azure.identity import DeviceCodeCredential
import json
import pandas as pd
import os
import requests
import concurrent.futures
from tqdm import tqdm
import pickle
from datetime import date, datetime, timedelta
from bs4 import BeautifulSoup
import dateutil.parser as parser 
import pytz
from pytz import timezone


desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') 

session_file = os.path.abspath(os.path.dirname(__file__)) + "\..\session\kusto.pkl"
tenant_id = "bcf2d2a2-2dee-419b-971f-21e5170fbf84"
KUSTO_URI = "https://kvcw1z66xgnuy00q1uhhzs.australiaeast.kusto.windows.net"
KUSTO_INGEST_URI = "https://ingest-kvcw1z66xgnuy00q1uhhzs.australiaeast.kusto.windows.net"

class DataIngestion():
    def __init__(self, kusto_uri=KUSTO_URI, kusto_ingest_uri=KUSTO_INGEST_URI, tenant_id=tenant_id):
        device_credential  = DeviceCodeCredential(authority="https://login.microsoftonline.com/", tenant_id=tenant_id)
        if os.path.exists(os.path.abspath(session_file)):
            with open(session_file, 'rb') as f:
                self.token = pickle.load(f)  
        else: 
            self.token = device_credential.get_token("https://help.kusto.windows.net/.default").token
            with open(session_file, 'wb') as f:
                pickle.dump(self.token, f)  
        kcsb_query = KustoConnectionStringBuilder.with_aad_device_authentication(KUSTO_URI, self.token)
        kcsb_ingest = KustoConnectionStringBuilder.with_aad_device_authentication(KUSTO_INGEST_URI, self.token)
        kcsb_query.authority_id = tenant_id
        kcsb_ingest.authority_id = tenant_id
        self.client_query = KustoClient(kcsb_query)
        self.client_ingest = QueuedIngestClient(kcsb_ingest)

    def ingest_raw(self, data, ingestion_props):
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for data_element in tqdm(data):
                df = pd.DataFrame({"raw": [json.dumps(data_element)]})
                future = executor.submit(self.client_ingest.ingest_from_dataframe(df, ingestion_props))
                futures.append(future)

    def ingest_events(self, data, database="Incidents", table="Raw"):
  
        check_changes = '''
        Raw
        | extend a = parse_json(Events)
        | distinct items= tostring(a)
        | extend a = parse_json(items)
        | project IncidentId=toint(a.IncidentId), Status=toint(a.Status)
        | sort by IncidentId desc 
        '''
        response = self.client_query.execute(database, check_changes)
        
        results = response.primary_results[0]

        set1 = set(json.dumps({"id":x["IncidentId"], "value": x["Status"]}, sort_keys=True) for x in results) #Serialize
        set2 = set(json.dumps({"id":x["IncidentId"], "value": x["Status"]}, sort_keys=True) for x in data)    #Serialize

        diff = [json.loads(x)["id"] for x in set2.difference(set1)]    #Deserialize

        diff = ', '.join(str(i) for i in diff)

        if diff:
            remove_list = '''
            .delete table Raw records <|
            Raw
            | extend item = parse_json(Events)
            | where toint(item.IncidentId) in (''' + diff + ''')
            '''
            response = self.client_query.execute(database, remove_list)

        incident_list = ''' 
        Raw
        | extend a = parse_json(Events)
        | distinct items= tostring(a)
        | extend a = parse_json(items)
        | project toint(a.IncidentId)
        ''' 
        response = self.client_query.execute(database, incident_list)        
        event_ids = [i[0] for i in response.primary_results[0].raw_rows]

        to_ingest = [i["IncidentId"] for i in data]

    #    unique = sorted(list(set(ids).difference(to_ingest)))
        similar = sorted(list(set(event_ids).intersection(to_ingest)))

        for i in data[:]:
            if i["IncidentId"] in similar:
                data.remove(i)

        path = os.path.join(desktop, "incidents.tmp")
        with open(path, "w") as file:
            for item in data:
                file.write(json.dumps(item) + "\n")
        if data:
            ingestion_props = IngestionProperties(database=database,table=table,data_format=DataFormat.MULTIJSON, ingestion_mapping_reference="RawEventMapping")
            self.client_ingest.ingest_from_file(path, ingestion_properties=ingestion_props)
        os.remove(path)
        return [i["IncidentId"] for i in data]

    def check_ingest_mfastats_tag(self, database="Incidents", table="Authentication"):
        tag = date.today().strftime("%Y-%m-%d")
        
        current_tags = ''' Authentication
        | extend tags = tostring(extent_tags())
        | distinct tags
        | extend item = parse_json(tags)
        | mv-expand tag = item
        | project trim_start("ingest-by:", tostring(tag))
        '''
        response = self.client_query.execute(database, current_tags)        
        tags = [i[0] for i in response.primary_results[0].raw_rows]
        for i in tags:
            if tag == i:
                return True
        return False

    def ingest_mfastats(self, data, database="Incidents", table="Authentication"):
        tag = date.today().strftime("%Y-%m-%d")

        path = os.path.join(desktop, "authentication.tmp")
        with open(path, "w") as file:
            for item in data:
                file.write(json.dumps(item) + "\n")
        if data:
            ingestion_props = IngestionProperties(database=database,table=table,data_format=DataFormat.MULTIJSON, ingestion_mapping_reference="AuthenticationMapping", ingest_if_not_exists=[tag],ingest_by_tags=[tag], drop_by_tags=[tag])
            self.client_ingest.ingest_from_file(path, ingestion_properties=ingestion_props)
        os.remove(path)

    def ingest_audit_logs(self, data, database="Incidents", table="AuditHistory"):
        to_ingest = [i["id"] for i in data]
        pending = ', '.join(str(i) for i in to_ingest)
        if not pending:
            return data
        remove_list = '''
        .delete table AuditHistory records <|
        AuditHistory
        | extend item = parse_json(Items)
        | where toint(item.id) in (''' + pending + ''')
        '''
        response = self.client_query.execute(database, remove_list)

        path = os.path.join(desktop, "audit.tmp")
        with open(path, "w") as file:
            for item in data:
                file.write(json.dumps(item) + "\n")
        if data:
            ingestion_props = IngestionProperties(database=database,table=table,data_format=DataFormat.MULTIJSON, ingestion_mapping_reference="AuditHistoryMapping")
            self.client_ingest.ingest_from_file(path, ingestion_properties=ingestion_props)
        os.remove(path)
        return data    

    def check_ingest_users_tag(self, database="Incidents", table="AzureAD"):
        tag = date.today().strftime("%Y-%m-%d")

        current_tags = '''
        AzureAD
        | extend tags = tostring(extent_tags())
        | distinct tags
        | extend item = parse_json(tags)
        | mv-expand tag = item
        | project trim_start("ingest-by:", tostring(tag))
        '''
        response = self.client_query.execute(database, current_tags)        
        tags = [i[0] for i in response.primary_results[0].raw_rows]
        for i in tags:
            if tag == i:
                return True
        return False

    def ingest_users(self, data, database="Incidents", table="AzureAD"):
        tag = date.today().strftime("%Y-%m-%d")

        path = os.path.join(desktop, "users.tmp")
        with open(path, "w") as file:
            for item in data:
                file.write(json.dumps(item) + "\n")
        if data:
            ingestion_props = IngestionProperties(database=database,table=table,data_format=DataFormat.MULTIJSON, ingestion_mapping_reference="FlatEventMapping", ingest_if_not_exists=[tag],ingest_by_tags=[tag], drop_by_tags=[tag])
            self.client_ingest.ingest_from_file(path, ingestion_properties=ingestion_props)
        os.remove(path)

    def check_ingest_devices_tags(self, database="Incidents", table="IntuneDevices"):
        tag = date.today().strftime("%Y-%m-%d")

        current_tags = '''
        IntuneDevices
        | extend tags = tostring(extent_tags())
        | distinct tags
        | extend item = parse_json(tags)
        | mv-expand tag = item
        | project trim_start("ingest-by:", tostring(tag))
        '''
        response = self.client_query.execute(database, current_tags)        
        tags = [i[0] for i in response.primary_results[0].raw_rows]
        for i in tags:
            if tag == i:
                return True
        return False

    def ingest_devices(self, data, database="Incidents", table="IntuneDevices"):
        tag = date.today().strftime("%Y-%m-%d")

        path = os.path.join(desktop, "devices.tmp")
        with open(path, "w") as file:
            for item in data:
                file.write(json.dumps(item) + "\n")
        if data:
            ingestion_props = IngestionProperties(database=database,table=table,data_format=DataFormat.MULTIJSON, ingestion_mapping_reference="IntuneDevicesMapping", ingest_if_not_exists=[tag],ingest_by_tags=[tag], drop_by_tags=[tag])
            self.client_ingest.ingest_from_file(path, ingestion_properties=ingestion_props)
        os.remove(path)

    def check_ingest_managed_devices_tag(self, database="Incidents", table="ManagedDevices"):
        tag = date.today().strftime("%Y-%m-%d")

        current_tags = '''
        ManagedDevices
        | extend tags = tostring(extent_tags())
        | distinct tags
        | extend item = parse_json(tags)
        | mv-expand tag = item
        | project trim_start("ingest-by:", tostring(tag))
        '''
        response = self.client_query.execute(database, current_tags)        
        tags = [i[0] for i in response.primary_results[0].raw_rows]
        for i in tags:
            if tag == i:
                return True
        return False

    def ingest_managed_devices(self, data, database="Incidents", table="ManagedDevices"):
        tag = date.today().strftime("%Y-%m-%d")

        path = os.path.join(desktop, "managedDevices.tmp")
        with open(path, "w") as file:
            for item in data:
                file.write(json.dumps(item) + "\n")
        if data:
            ingestion_props = IngestionProperties(database=database,table=table,data_format=DataFormat.MULTIJSON, ingestion_mapping_reference="ManagedDevicesMapping", ingest_if_not_exists=[tag],ingest_by_tags=[tag], drop_by_tags=[tag]) 
            self.client_ingest.ingest_from_file(path, ingestion_properties=ingestion_props)
        os.remove(path)

    def check_defender_agents_tag(self, database="Incidents", table="DefenderAgents"):
        tag = date.today().strftime("%Y-%m-%d")
        current_tags = '''
        DefenderAgents
        | extend tags = tostring(extent_tags())
        | distinct tags
        | extend item = parse_json(tags)
        | mv-expand tag = item
        | project trim_start("ingest-by:", tostring(tag))
        '''
        response = self.client_query.execute(database, current_tags)        
        tags = [i[0] for i in response.primary_results[0].raw_rows]
        for i in tags:

            if tag == i:
                return True
        return False

    def ingest_defender_agents(self, path, database="Incidents", table="DefenderAgents"):
        tag = date.today().strftime("%Y-%m-%d")

        ingestion_props =  IngestionProperties(database=database,table=table,data_format=DataFormat.CSV, ingestion_mapping_reference="DefenderAgents_mapping", additional_properties={'ignoreFirstRecord': 'true'},  ingest_if_not_exists=[tag],ingest_by_tags=[tag], drop_by_tags=[tag]) 
        result = self.client_ingest.ingest_from_file(path, ingestion_properties=ingestion_props)
        os.remove(path)
        return result   

    def check_signin_last_timestamp(self, database="Incidents", table= "SignInLogs"):

        created_datetime = '''
        let abc = SignInLogs
        | distinct ingestion_time()
        | summarize max($IngestionTime);
        SignInLogs
        | where ingestion_time() == toscalar(abc)
        | project item = parse_json(Items)
        | sort by todatetime(item.createdDateTime) desc 
        | take 1
        | project upper=todatetime(item.createdDateTime)
        '''
        response = self.client_query.execute(database, created_datetime)  
        t_lower = response.primary_results[0].rows[0]["upper"]
        lower_limit = (t_lower + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        return lower_limit.strftime("%Y-%m-%dT%H:%M:%SZ")

    def ingest_signin_logs(self, data, database="Incidents", table= "SignInLogs"):
        
        path = os.path.join(desktop, "signIns.tmp")
        with open(path, "w") as file:
            for item in data:
                file.write(json.dumps(item) + "\n")
        if data:
            ingestion_props = IngestionProperties(database=database,table=table,data_format=DataFormat.MULTIJSON, ingestion_mapping_reference="SignInLogsMapping") 
            self.client_ingest.ingest_from_file(path, ingestion_properties=ingestion_props)
        os.remove(path)

    def get_latest_av_engines(self):

        defender_updates = "https://www.microsoft.com/en-us/wdsi/defenderupdates/"
        
        response = requests.get(defender_updates, headers={"User-Agent" : "PostmanRuntime/7.32.2"})
        soup = BeautifulSoup(response.content, 'html.parser')

        ul_tag = soup.find("ul", {"class" : "c-list list-bottom-margin"})
        version_info = {}
        for i in ul_tag.find_all("li"):
                if "Version" == i.text.split(": ", 1)[0]:
                    version_info["SignatureVersion"] =  i.text.split(": ", 1)[1]
                elif "Engine Version" == i.text.split(": ", 1)[0]:
                    version_info["EngineVersion"] = i.text.split(": ", 1)[1]
                elif "Platform Version" ==  i.text.split(": ", 1)[0]:
                    version_info["PlatformVersion"] = i.text.split(": ", 1)[1]
                elif "Released" == i.text.split(": ", 1)[0]:
                    dt = parser.parse(i.text.split(": ", 1)[1])
                    local_tz = pytz.timezone('Asia/Singapore')
                    utc_time = local_tz.localize(dt).astimezone(pytz.UTC)
                    version_info["ReleaseDateUtc"] = utc_time.strftime("%Y-%m-%dT%H:%M")

        return version_info

    def check_latest_av_engines(self, database="Incidents", table= "AVEngineVersion"):

        latest_release = '''
        AVEngineVersion
        | extend item = parse_json(Items)
        | extend release = todatetime(item.ReleaseDateUtc)
        | summarize latest=max(release)
        '''
        response = self.client_query.execute(database, latest_release)        
        latest_date = response.primary_results[0].raw_rows[0]

        if latest_date:
            return latest_date[0]
        else:
            return

    def ingest_latest_av_engine(self, data, database="Incidents", table= "AVEngineVersion"):

        path = os.path.join(desktop, "av.tmp")
        with open(path, "w") as file:
            file.write(json.dumps(data))
        if data:
            ingestion_props = IngestionProperties(database=database,table=table,data_format=DataFormat.JSON, ingestion_mapping_reference="AVEngineVersionMapping")
            self.client_ingest.ingest_from_file(path, ingestion_properties=ingestion_props)
        os.remove(path)

    def get_latest_compliance_ingestion_time(self, database="Incidents", table= "CompliancePolicy"):

        t_latest = datetime.now(pytz.utc)
#        latest_date = (t_latest + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        latest_date = t_latest.replace(hour=0, minute=0, second=0, microsecond=0)
#        latest_date =t_latest.replace(day=t_latest.day+1, hour=0, minute=0, second=0, microsecond=0)

        latest_compliance_ingestion_time = '''
        CompliancePolicy
        | summarize out=max(ingestion_time())
        | take 1
        '''
        response = self.client_query.execute(database, latest_compliance_ingestion_time)        
        current_date = response.primary_results[0].rows[0]["out"]

        if not current_date or (current_date.replace(hour=0, minute=0, second=0, microsecond=0) < latest_date):
            return True 
        else:
            return False

    def ingest_compliance_policy(self, data, database="Incidents", table = "CompliancePolicy"):

        path = os.path.join(desktop, "compliance_policy.tmp")
        with open(path, "w") as file:
            for item in data:
                file.write(json.dumps(item) + "\n")
        if data:
            ingestion_props = IngestionProperties(database=database,table=table,data_format=DataFormat.MULTIJSON, ingestion_mapping_reference="CompliancePolicyMapping")
            self.client_ingest.ingest_from_file(path, ingestion_properties=ingestion_props)
        os.remove(path)    


    def ingest_device_inventory(self, data, database="Incidents", table="DeviceInventory"):
        tag = date.today().strftime("%Y-%m-%d")

        path = os.path.join(desktop, "devices_inventory.tmp")
        with open(path, "w") as file:
            for item in data:
                file.write(json.dumps(item) + "\n")
        if data:
            ingestion_props = IngestionProperties(database=database,table=table,data_format=DataFormat.MULTIJSON, ingestion_mapping_reference="DeviceInventoryMapping", ingest_if_not_exists=[tag],ingest_by_tags=[tag], drop_by_tags=[tag])
            self.client_ingest.ingest_from_file(path, ingestion_properties=ingestion_props)
        os.remove(path)

    def check_device_inventory_tag(self, database="Incidents", table="DeviceInventory"):
        tag = date.today().strftime("%Y-%m-%d")

        current_tags = '''
        DeviceInventory
        | extend tags = tostring(extent_tags())
        | distinct tags
        | extend item = parse_json(tags)
        | mv-expand tag = item
        | project trim_start("ingest-by:", tostring(tag))
        '''
        response = self.client_query.execute(database, current_tags)        
        tags = [i[0] for i in response.primary_results[0].raw_rows]
        for i in tags:
            if tag == i:
                return True
        return False


    def check_raw_audit_list(self, database="Incidents", table="RawAuditHistory"):
        latest_id = '''
        RawAuditHistory
        | extend Items = parse_json(Items)
        | project id=toint(Items.auditId)
        '''
        response = self.client_query.execute(database, latest_id)        
#        audit_id = response.primary_results[0].raw_rows[0]
        audit_id = [i[0] for i in response.primary_results[0].raw_rows]

        if audit_id:
            return audit_id
        else:
            return

    def ingest_raw_audit_history(self, data, database="Incidents", table="RawAuditHistory"):

        audit_id = self.check_raw_audit_list()

        for i in data[:]:
            if i["auditId"] in audit_id:
                data.remove(i)

        path = os.path.join(desktop, "raw_audit_history.tmp")
        with open(path, "w") as file:
            for item in data:
                file.write(json.dumps(item) + "\n")
        if data:
            ingestion_props = IngestionProperties(database=database,table=table,data_format=DataFormat.MULTIJSON, ingestion_mapping_reference="RawAuditHistoryMapping")
            self.client_ingest.ingest_from_file(path, ingestion_properties=ingestion_props)
        os.remove(path)


