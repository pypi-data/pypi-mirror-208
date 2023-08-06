import os, sys, time, io
import requests, json, pickle, ast, zipfile, re
from urllib.parse import urlparse, parse_qs
sys.path.append("..") # Adds higher directory to python modules path.
from config.config import *
from helper import login
from loguru import logger
from urllib.parse import parse_qs, urlsplit, parse_qsl
from datetime import datetime, timedelta

#dbgPrint = PyLog(__name__, level=logging.INFO)

logger.add(f"./logs/{__name__}.log", backtrace=True, diagnose=True, filter="MSGraphApi")
dbgPrint = logger
#dbgPrint.disable(__name__)

class MSGraphApi:
    def __init__(self, email=None, **kwargs):
        self._session = requests.Session()
#        self.auth_page = 'https://portal.azure.com/api/DelegationToken'
        self.auth_page = 'https://endpoint.microsoft.com/api/DelegationToken'
#        self.auth_page = 'https://portal.azure.com/api/DelegationToken?feature.cacheextensionapp=true&feature.internalgraphapiversion=true&feature.tokencaching=true'
        self.headers = kwargs.get('headers', {'content-type' : 'application/json'})
        self.cookies = kwargs.get('cookies', {})
#        self.auth_folder = kwargs.get('output', "")
        self.body = kwargs.get('json', '')

        self.users_auth = ""
        self.iam_auth = ""
        self.devices_auth = ""
        self.email = email

        self._portalAuthorization = {}
        self._altPortalAuthorization = {}
        self._session.cookies.update(self.cookies)
        self._session.headers.update(self.headers)
        if self.cookies:
            self._authorization = json.loads(self.tryrequest(self.auth_page, json=self.body).text)
#            self._authorization = json.loads(self._session.post(self.auth_page, json=self.body).text)

       #     self._authorization = json.loads(self._session.post(self.auth_page, json=self.body).text)
   
   
    def tryrequest(self, arg, **kwargs):
        dbgPrint.debug("sending request...")
        headers = kwargs.pop('headers', {})  
        params = kwargs.pop('params', {})
        data  = kwargs.pop('json', {})

        if kwargs:
            dbgPrint.error("Unexpected argument")
            raise("Unexpected **kwargs argument")
#        response = requests.models.Response
        for i in range(10):
            try:
                if params or (not data):
                    response = self._session.get(arg, headers=headers, params=params, verify=False)
                    if response.status_code == 440:
                        login.Login().delete_session()
                        login.Login(self.email).login()
                        self.load_session()
                        continue
                    elif response.status_code == 401:
                        break
                    elif response.status_code == 200:
                        break
                    elif response.status_code == 500:
                        message = json.loads(response.text)
                        dbgPrint.error(message["Message"])
                    elif response.status_code == 503:
                        dbgPrint.error("Service Unavailable")
                        continue
                    elif response.status_code == 504:
                        dbgPrint.error("Gateway Time-out")
                    elif response.status_code == 429:
                        message = json.loads(response.text)
                        dbgPrint.error(message["error"]["message"])
                        continue
                else:
                    response = self._session.post(arg, headers=headers, json=data, verify=False)
                    if response.status_code == 440 or response.status_code == 404 or response.status_code == 400:
                        login.Login().delete_session()
                        login.Login(self.email).login()
                        self.load_session()
                        continue
                    elif response.status_code == 200 or response.status_code == 201:
                        break
                    elif response.status_code == 429:
                        message = json.loads(response.text)
                        dbgPrint.error(message["error"]["message"])
                    elif response.status_code == 500:
                        message = json.loads(response.text)
                        dbgPrint.error(message["Message"])
                    elif response.status_code == 504:
                        dbgPrint.error("Gateway Time-out")
      
            except:
                continue
        return response            

    def get_aad_authorization(self):
        
        json_data = {
        'extensionName': 'Microsoft_AAD_UsersAndTenants',
        'resourceName': 'microsoft.graph',
        'tenant': TENANT_ID,
        'portalAuthorization': self._authorization['portalAuthorization'],
        'altPortalAuthorization': self._authorization['altPortalAuthorization']
        }

        response = self._session.post(self.auth_page, json=json_data, verify=False)

        for _ in range(5):
            if response.status_code == 440:
#                raise Exception("Reset")
                Login.Login().delete_session()
                Login.Login(self.email).login()
                self.load_session()
                response = self._session.post(self.auth_page, json=json_data, verify=False)                      #Need exception handling
                if response.status_code == 200:
                    break
            elif response.status_code == 200:
                break

            elif response.status_code == 500:
                message = json.loads(response.text)
                dbgPrint.error(message["Message"])
                sys.exit()

        bearer = json.loads(response.text)
        users_auth = bearer["value"]["authHeader"]

        return users_auth

    def get_intune_authorization(self):

        json_data = {
        'extensionName': 'Microsoft_Intune_DeviceSettings',
        'resourceName': 'microsoft.graph',
        'tenant': TENANT_ID,
        'portalAuthorization': self._authorization['portalAuthorization'],
        'altPortalAuthorization': self._authorization['altPortalAuthorization']
        }

        response = self._session.post(self.auth_page, json=json_data, verify=False)
        bearer = json.loads(response.text)
        intune_auth = bearer["value"]["authHeader"]
        return intune_auth

    def get_iam_authorization(self):
        json_data = {
        'extensionName': 'Microsoft_AAD_IAM',
        'resourceName': 'microsoft.graph',
        'tenant': TENANT_ID,
        'portalAuthorization': self._authorization['portalAuthorization'],
        'altPortalAuthorization': self._authorization['altPortalAuthorization']
        }

        response = self._session.post(self.auth_page, json=json_data, verify=False)
        bearer = json.loads(response.text)
        iam_auth = bearer["value"]["authHeader"]
        return iam_auth

    def get_enrollment_authorization(self):

        json_data = {
        'extensionName': 'Microsoft_Intune_Enrollment',
        'resourceName': 'microsoft.graph',
        'tenant': TENANT_ID,
        'portalAuthorization': self._authorization['portalAuthorization'],
        'altPortalAuthorization': self._authorization['altPortalAuthorization']        
        }

        response = self.tryrequest(self.auth_page, json=json_data)
        bearer = json.loads(response.text)
        enrollment_auth = bearer["value"]["authHeader"]
        return enrollment_auth

    def save_session(self):

        session_path = os.path.abspath(os.path.dirname(__file__)) + "\..\session"
        session_file = session_path + "\\msgraph.pkl"

        if not os.path.exists(session_path):
            os.makedirs(session_path)
        with open(session_file, 'wb') as f:
            pickle.dump(self.cookies, f)
            pickle.dump(self.body, f)


    def load_session(self):

        session_path = os.path.abspath(os.path.dirname(__file__)) + "\..\session"
        session_file = session_path + "\\msgraph.pkl"

        if os.path.exists(session_file):
            with open(session_file, 'rb') as f:
                cookies = pickle.load(f)
                json_data = pickle.load(f)
            self.cookies = cookies
            self.body = json_data
            self.__init__(self.email, cookies=cookies, json=json_data)
            self.users_auth = self.get_aad_authorization()
            self.devices_auth = self.get_intune_authorization()
            self.iam_auth = self.get_iam_authorization()
            self.intune_enrollment_auth = self.get_enrollment_authorization()
        else:
            session = login.Login(self.email)
            session.delete_session()
            session.login()
            self.load_session()
        return self

    def search_user(self, username):

        microsoft_graph = 'https://graph.microsoft.com/beta/$batch'

        query = "(\"displayName:" + username + "\" OR \"mail:" + username + "\" OR \"userPrincipalName:" + username + "\" OR \"givenName:" + username +"\")"

        headers = {
        'Authorization': self.users_auth,
        'content-type': 'application/json'
        }

        json_data = {
        'requests': [
            {
            'id': "searched_user",
            'method': "GET",
            'url': "/users?$select=id," 
            "displayName,"
            "givenName,"
            "surname,"
            "userPrincipalName,"
            "userType,"
            "country,"
            "usageLocation,"
            "companyName"
            "&$search=" + query + "&$top=1&$count=true",
            
            'headers': {
                'ConsistencyLevel': "eventual",
                'x-ms-command-name': "UserManagement - ListUsers",
                        }
                    }
                ]
            }

        response = self.tryrequest(microsoft_graph, headers=headers, json=json_data)
#        response = self._session.post(microsoft_graph, headers=headers, json=json_data, verify=False)
        
        return (json.loads(response.text)['responses'][0]['body']['value'])

    def get_users_count(self):
        microsoft_graph = 'https://graph.microsoft.com/beta/$batch'
        headers = {
        'Authorization': self.users_auth,
        'content-type': 'application/json'
        }
        json_data = {
        'requests': [
            {
            'id': "searched_user",
            'method': "GET",
            'url': "/users?$select=id&$count=true",
            'headers': {
                'ConsistencyLevel': "eventual",
                'x-ms-command-name': "UserManagement - ListUsers",
                        }
                    }
                ]
            }
        response = self.tryrequest(microsoft_graph, headers=headers, json=json_data)
        if response.status_code == 200:
            object = json.loads(response.text)
            count = object["responses"][0]["body"]["@odata.count"]
        return count

    def get_all_users(self, skiptoken="", user_list=[]):
        microsoft_graph = 'https://graph.microsoft.com/beta/$batch'
        headers = {
        'Authorization': self.users_auth,
        'content-type': 'application/json'
        }
        if skiptoken:
            skiptoken = "&skiptoken=" + skiptoken

        json_data = {
        'requests': [
            {
            'id': "searched_user",
            'method': "GET",
            'url': "/users?"
            "$top=999"
            "&$count=true"
            "&$orderby=displayName asc"+skiptoken,
            'headers': {
                'ConsistencyLevel': "eventual",
                'x-ms-command-name': "UserManagement - ListUsers",
                        }
                    }
                ]
            }

        
        response = self.tryrequest(microsoft_graph, headers=headers, json=json_data)
        if response.status_code == 200:
            object = json.loads(response.text)
            nextlink = object["responses"][0]["body"].get("@odata.nextLink")
            if nextlink != None:
                user_list.extend(object["responses"][0]["body"]["value"])
                dbgPrint.info(len(user_list))
                skiptoken = dict(parse_qsl(urlsplit(nextlink).query)).get("$skiptoken") if dict(parse_qsl(urlsplit(nextlink).query)).get("$skiptoken") else dict(parse_qsl(urlsplit(nextlink).query)).get("skiptoken", "")
                self.get_all_users(skiptoken=skiptoken, user_list=user_list)
            else:
                user_list.extend(object["responses"][0]["body"]["value"])

        return user_list


    def search_device_by_name_beta(self,  device_name):
        microsoft_graph = 'https://graph.microsoft.com/beta/$batch'

        query = "/devices?$search=(\"displayName:" + device_name + "\")&$top=1&$count=true"

        json_data = {
        "requests": [
            {
            "id": "device_name",
            "method": "GET",
            "url": query,
            "headers": {
                "ConsistencyLevel": "eventual",
                "x-ms-command-name": "DeviceManagement - ListDevices",
                        }
                    }
                ]
            }

        headers = {
        'Authorization': self.devices_auth,
        'content-type': 'application/json'
        }

        response = self.tryrequest(microsoft_graph, headers=headers, json=json_data)
#        response = self._session.post(microsoft_graph, headers=headers, json=json_data, verify=False)

        return (json.loads(response.text)['responses'][0]['body']['value'])

    def search_device_by_name(self, device_name):

        microsoft_graph_device = 'https://graph.microsoft.com/beta/deviceManagement/managedDevices'

        query = "(Notes eq 'bc3e5c73-e224-4e63-9b2b-0c36784b7e80') and (contains(activationlockbypasscode, '" + device_name + "'))"

#        query = "(deviceName eq '" + device_name + "')"


        params = {
        '$filter'   :  query,
        '$Skip'     : '0',
        '$top'      : 25,           #Removing $top will result in undefined behavior
        '$select'   : "deviceName,managementAgent,ownerType,complianceState,deviceType,userId,userPrincipalName,osVersion,lastSyncDateTime,userPrincipalName,azureADDeviceId,id,deviceRegistrationState,managementState,exchangeAccessState,exchangeAccessStateReason,deviceActionResults,deviceEnrollmentType"
        }

        headers = {
        'Authorization': self.devices_auth,
        'content-type': 'application/json'
        }

        response = self.tryrequest(microsoft_graph_device, headers=headers, params=params)        
#        response = self._session.get(microsoft_graph_device, headers=headers, params=params, verify=False)

        return (json.loads(response.text))['value']

    def search_device_by_azure_id(self, senseMachineId):
        
        if senseMachineId == None or senseMachineId ==  "":
            return {}
        microsoft_graph_device = 'https://graph.microsoft.com/beta/deviceManagement/managedDevices'
        query = "(azureADDeviceId eq '" + senseMachineId + "')"

        params = {
        '$filter'   :  query,
        '$Skip'     : '0',
        '$top'      : 25,           #Removing $top will result in undefined behavior
        '$select'   : "deviceName,managementAgent,ownerType,complianceState,deviceType,userId,userPrincipalName,osVersion,lastSyncDateTime,userPrincipalName,azureADDeviceId,id,deviceRegistrationState,managementState,exchangeAccessState,exchangeAccessStateReason,deviceActionResults,deviceEnrollmentType"
        }

        headers = {
        'Authorization': self.devices_auth,
        'content-type': 'application/json'
        }

        response = self.tryrequest(microsoft_graph_device, headers=headers, params=params)

#        response = self._session.get(microsoft_graph_device, headers=headers, params=params, verify=False)

        return (json.loads(response.text))['value']


    def get_all_devices(self, skiptoken="", device_list=[]):
        microsoft_graph = 'https://graph.microsoft.com/beta/$batch'

        if skiptoken:
            skiptoken = "&skiptoken=" + skiptoken

        json_data = {
        "requests": [
            {
            "id": "device_name",
            "method": "GET",
            "url": "/devices?"
            "$count=true"
            "&$top=999" + skiptoken,
            "headers": {
                "ConsistencyLevel": "eventual",
                "x-ms-command-name": "DeviceManagement - ListDevices",
                        }
                    }
                ]
            }

        headers = {
        'Authorization': self.devices_auth,
        'content-type': 'application/json'
        }

        response = self.tryrequest(microsoft_graph, headers=headers, json=json_data)
        if response.status_code == 200:
            object = json.loads(response.text)
            nextlink = object["responses"][0]["body"].get("@odata.nextLink")
            if nextlink != None:
                device_list.extend(object["responses"][0]["body"]["value"])
                dbgPrint.info(len(device_list))
                skiptoken = dict(parse_qsl(urlsplit(nextlink).query)).get("$skiptoken") if dict(parse_qsl(urlsplit(nextlink).query)).get("$skiptoken") else dict(parse_qsl(urlsplit(nextlink).query)).get("skiptoken", "")
                self.get_all_devices(skiptoken=skiptoken, device_list=device_list)
            else:
                device_list.extend(object["responses"][0]["body"]["value"])

        return device_list


    def get_all_devices_beta(self, skiptoken=0, top=50, device_list=[]):
        microsoft_graph_device = 'https://graph.microsoft.com/beta/deviceManagement/managedDevices'
        query = "(Notes eq 'bc3e5c73-e224-4e63-9b2b-0c36784b7e80')"

        params = {
        '$filter'   :  query,
        '$skipToken': "Skip='" + str(skiptoken) + "'",
        '$top'      : top,           #Removing $top will result in undefined behavior
#        '$select'   : "deviceName,managementAgent,ownerType,complianceState,deviceType,userId,userPrincipalName,osVersion,lastSyncDateTime,userPrincipalName,azureADDeviceId,id,deviceRegistrationState,managementState,exchangeAccessState,exchangeAccessStateReason,deviceActionResults,deviceEnrollmentType"
        }

        headers = {
        'Authorization': self.devices_auth,
        'content-type': 'application/json'
        }

        response = self.tryrequest(microsoft_graph_device, headers=headers, params=params)
        if response.status_code == 200:
            object = json.loads(response.text)
            nextlink = object.get("@odata.nextLink")
            count = object.get("@odata.count")
            if count == top:
                device_list.extend(object["value"])
                dbgPrint.info(len(device_list))
                self.get_all_devices_beta(skiptoken=skiptoken+top, device_list=device_list)
            else:
                device_list.extend(object["value"])
                dbgPrint.info(len(device_list))
        return device_list

    def get_user_groups(self, userPrincipalName):
        user_object = self.search_user(userPrincipalName)

        user_groups = 'https://graph.microsoft.com/beta/users/' + user_object[0]["id"] + '/memberOf/$/microsoft.graph.group'


        params = {
            '$select' : "id, displayName, securityEnabled",
            '$top'    : 5,
            '$filter' : "(mailEnabled eq false and securityEnabled eq true)",
            '$count'  : "true"
            }
        
        headers = {
            'Authorization' : self.users_auth,
            'content-type' : 'application/json',
            'ConsistencyLevel' : 'eventual'
            }

        response = self.tryrequest(user_groups, headers=headers, params=params)

        return [i['displayName'] for i in json.loads(response.text)['value'] if re.search("[A-Z]{3,5}\_",i['displayName'])]

    #Need exception

    def get_defender_agents(self):

        cache_report = "https://graph.microsoft.com/beta/deviceManagement/reports/cachedReportConfigurations"
        id = "DefenderAgents_00000000-0000-0000-0000-000000000002"

        json_data = {
        "id": id,
        "filter": "",
        "orderBy": [],
        "select": [
            "DeviceName",
            "DeviceState",
            "_ManagedBy",
            "AntiMalwareVersion",
            "CriticalFailure",
            "ProductStatus",
            "TamperProtectionEnabled",
            "IsVirtualMachine",
            "IsWDATPSenseRunning",
            "WDATPOnboardingState",
            "EngineVersion",
            "FullScanOverdue",
            "FullScanRequired",
            "LastFullScanDateTime",
            "LastQuickScanDateTime",
            "LastQuickScanSignatureVersion",
            "LastReportedDateTime",
            "MalwareProtectionEnabled",
            "NetworkInspectionSystemEnabled",
            "PendingFullScan",
            "PendingManualSteps",
            "PendingOfflineScan",
            "PendingReboot",
            "QuickScanOverdue",
            "RealTimeProtectionEnabled",
            "RebootRequired",
            "SignatureUpdateOverdue",
            "SignatureVersion",
            "UPN",
            "UserEmail",
            "UserName"
        ],
        "metadata": "=>filterPicker=dW5kZWZpbmVk"
        }
        self.intune_enrollment_auth = self.get_enrollment_authorization()
        headers = {
        'Authorization': self.intune_enrollment_auth,
        'content-type': 'application/json'
        }

        result = self.tryrequest(cache_report, headers=headers, json=json_data)
        status = json.loads(result.text)["status"]
        
        while (status != "completed"):
            dbgPrint.debug(status)
            cache_report_config = cache_report + "('" + id + "')"
            result = self.tryrequest(cache_report_config, headers=headers)
            status = json.loads(result.text)["status"]
            time.sleep(1)

        dbgPrint.debug(status)
        defender_agents = self.export_job_reports(id)

        return defender_agents


    def export_job_reports(self, id):

        export_job = "https://graph.microsoft.com/beta/deviceManagement/reports/exportJobs"
        headers = {
        'Authorization': self.intune_enrollment_auth,
        'content-type': 'application/json'
        }

        json_data = {
        "reportName": "DefenderAgents",
        "filter": "",
        "select": [
            "DeviceName",
            "DeviceState",
            "_ManagedBy",
            "AntiMalwareVersion",
            "CriticalFailure",
            "ProductStatus",
            "TamperProtectionEnabled",
            "IsVirtualMachine",
            "IsWDATPSenseRunning",
            "WDATPOnboardingState",
            "EngineVersion",
            "FullScanOverdue",
            "FullScanRequired",
            "LastFullScanDateTime",
            "LastQuickScanDateTime",
            "LastQuickScanSignatureVersion",
            "LastReportedDateTime",
            "MalwareProtectionEnabled",
            "NetworkInspectionSystemEnabled",
            "PendingFullScan",
            "PendingManualSteps",
            "PendingOfflineScan",
            "PendingReboot",
            "QuickScanOverdue",
            "RealTimeProtectionEnabled",
            "RebootRequired",
            "SignatureUpdateOverdue",
            "SignatureVersion",
            "UPN",
            "UserEmail",
            "UserName"
        ],
        "format": "csv",
        "snapshotId": id
        }

        result = self.tryrequest(export_job, headers=headers, json=json_data)
        object = json.loads(result.text)
        id = object["id"]

        export_job_result = export_job + "('" + id + "')"

        status = ""

        result = self.tryrequest(export_job_result, headers=headers)
        object = json.loads(result.text)
        status = object["status"]
        while status != "completed":
            dbgPrint.debug(status)
            result = self.tryrequest(export_job_result, headers=headers)
            object = json.loads(result.text)
            status = object["status"]        
        

        desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') 
        dbgPrint.debug(status)
        agents_file = self.tryrequest(object["url"])
        dbgPrint.debug(object["url"])
        z = zipfile.ZipFile(io.BytesIO(agents_file.content))
        z.extract(id+".csv", path=desktop)
        return os.path.join(desktop, id + ".csv")


    def check_mfa_status(self, userPrincipalName):
        mfa_status = 'https://graph.microsoft.com/beta/reports/credentialUserRegistrationDetails'
        params = {'$filter' : "userPrincipalName eq '" + userPrincipalName + "'"}
        headers = {
        'Authorization': self.iam_auth,
        'content-type': 'application/json'
        }
        response = self.tryrequest(mfa_status, headers=headers, params=params)

#        response = self._session.get(mfa_status, headers=headers, params=params, verify=False)
        return json.loads(response.text).get('value', {})

    def get_users_mfa(self, skiptoken="", top=50, mfa_list=[]):
        mfa_status = 'https://graph.microsoft.com/beta/reports/credentialUserRegistrationDetails'
        params = {'$filter' : ""}

        if skiptoken:
            params["$skiptoken"] = skiptoken

        headers = {
        'Authorization': self.iam_auth,
        'content-type': 'application/json'
        }
        response = self.tryrequest(mfa_status, headers=headers, params=params)
        while(response.status_code != 200):
            if response.status_code == 401:
                self.iam_auth=self.get_iam_authorization()
                headers = {
                'Authorization': self.iam_auth,
                'content-type': 'application/json'
                }
                response = self.tryrequest(sign_ins, headers=headers, params=params)

        if response.status_code == 200:
            object = json.loads(response.text)
            nextlink = object.get("@odata.nextLink")
            if nextlink != None:
                mfa_list.extend(object["value"])
                dbgPrint.info(len(mfa_list))
                skiptoken = dict(parse_qsl(urlsplit(nextlink).query)).get("$skiptoken") if dict(parse_qsl(urlsplit(nextlink).query)).get("$skiptoken") else dict(parse_qsl(urlsplit(nextlink).query)).get("skiptoken", "")
                self.get_users_mfa(skiptoken=skiptoken, mfa_list=mfa_list)
            else:
                mfa_list.extend(object["value"])
                dbgPrint.info(len(mfa_list))
        return mfa_list

    def get_signin_logs(self, result=[], top=1000, skiptoken="", min="", max=""):
        
        sign_ins = "https://graph.microsoft.com/beta/auditLogs/signIns"

        params = {
            "api-version"   : "beta", 
            "$filter"       : "(createdDateTime ge "+ min +" and createdDateTime lt " + max + ")",
            "$top"          : top,
            "$orderby"      : "createdDateTime desc",
            "source"        : "kds"
        }
        if skiptoken:
            params["$skiptoken"] = skiptoken


        headers = {
        'Authorization': self.iam_auth,
        'content-type': 'application/json'
        }


        response = self.tryrequest(sign_ins, headers=headers, params=params)
        while(response.status_code != 200):
            if response.status_code == 401:
                self.iam_auth=self.get_iam_authorization()
                headers = {
                'Authorization': self.iam_auth,
                'content-type': 'application/json'
                }
                response = self.tryrequest(sign_ins, headers=headers, params=params)

        if response.status_code == 200:
            object = json.loads(response.text)
            nextlink = object.get("@odata.nextLink")
            if nextlink != None:
                result.extend(object["value"])
                dbgPrint.info(len(result))
                skiptoken = dict(parse_qsl(urlsplit(nextlink).query)).get("$skiptoken") if dict(parse_qsl(urlsplit(nextlink).query)).get("$skiptoken") else dict(parse_qsl(urlsplit(nextlink).query)).get("skiptoken", "")
                return skiptoken
            else:
                result.extend(object["value"])
                dbgPrint.info(len(result))

    def get_all_signins(self, login_logs=[], top=1000, min="", max=""):
        now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)

        if not min:
            t_lower = now - timedelta(days=30)
            t_lower = t_lower.replace(minute=0, second=0, microsecond=0, hour=t_lower.hour+1)
            t_upper = t_lower + timedelta(hours=1)
        else:
            t_lower = datetime.strptime(min, "%Y-%m-%dT%H:%M:%SZ")
            t_lower = t_lower.replace(minute=0, second=0, microsecond=0)
            t_upper = t_lower + timedelta(hours=1)

        if now < t_upper:
            return None

        lower_limit = t_lower.strftime("%Y-%m-%dT%H:%M:%SZ")
        upper_limit = t_upper.strftime("%Y-%m-%dT%H:%M:%SZ")

        skiptoken = self.get_signin_logs(result=login_logs, top=top, min=lower_limit, max=upper_limit)

        while(skiptoken):
            dbgPrint.info(skiptoken)
            skiptoken = self.get_signin_logs(result=login_logs, top=top, skiptoken=skiptoken, min=lower_limit, max=upper_limit)

        return upper_limit

    
    def get_compliance_policy(self):
        device_compliance = "https://graph.microsoft.com/beta/deviceManagement/deviceCompliancePolicies"

        headers = {
            "Authorization" : self.devices_auth
        }

        response = self.tryrequest(device_compliance, headers=headers)
        for i in range(3):
            if response.status_code == 200: 
                break
            elif response.status_code == 401:
                self.devices_auth = self.get_intune_authorization()
                headers = {
                    "Authorization" : self.devices_auth
                }
                response = self.tryrequest(device_compliance, headers=headers)

        result = json.loads(response.text)["value"]
        return result

