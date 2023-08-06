import requests
import xmltodict
import os, sys
import pickle
from loguru import logger



logger.add(f"./logs/{__name__}.log", backtrace=True, diagnose=True, level="DEBUG", filter=__name__)
dbgPrint = logger
dbgPrint.disable(__name__)

sys.path.append("..") # Adds higher directory to python modules path.
from helper import login

class MultiFactor:
    def __init__(self, email=None, **kwargs):
        self._email = email
        self._cookies = kwargs.pop('cookies', {})                         #dictionary
        self._headers = kwargs.pop('headers', {'content-type' : 'application/json'})
        self._session = requests.Session()
        self._session.cookies.update(self._cookies)
        self._session.headers.update(self._headers)
        pass

    def save_session(self):
        session_path = os.path.abspath(os.path.dirname(__file__)) + "\..\session"
        session_file = session_path + "\\mfa.pkl"
        if not os.path.exists(session_path):
            os.makedirs(session_path)
        else:
            with open(session_file, 'wb') as f:
                pickle.dump(self._cookies, f)
                pickle.dump(self._headers, f)

    def load_session(self):
        session_path = os.path.abspath(os.path.dirname(__file__)) + "\..\session"
        session_file = session_path + "\\mfa.pkl"
        if os.path.exists(session_file):
            dbgPrint.debug("[+] Loading " + session_file)
            with open(session_file, 'rb') as f:
                cookies = pickle.load(f)
                headers = pickle.load(f)
            self.__init__(self._email, cookies=cookies, headers=headers)
            return self
        else:
            login.Login().delete_session()
            login.Login(self.email).login()
            self.load_session()
            return self

    def reset_session(self, email):
        login.Login().mfa_login(email)

    def query_user(self, user):
        mfa_page = 'https://account.activedirectory.windowsazure.com/usermanagement/GenericFetchData.ajax'

        data = {
            "p0":"Microsoft.Online.BOX.Admin.UI.UserManagement.MultifactorVerification.FetchUsers",
            "p1":"",
            "p2":"{\"SortProperty\":\"\",\"SortOrder\":0}",
            "p3":"1",
            "p4":"{\"FilterID\":null,\"FilterType\":\"10\",\"SearchText\":\"" + user + "\",\"MfaState\":\"Any\"}",
            "assembly":"BOX.UI, Version=2.0.0.0, Culture=neutral, PublicKeyToken=null",
            "class":"Microsoft.Online.BOX.UI.WebControls.ListGrid"
        }

        response = self._session.get(mfa_page, data=data, verify=False)
        if "SessionValid" in response.text:
            object = xmltodict.parse(response.text.strip("SessionValid"))['response']['Items']
            if object.get('Item'): 
                if isinstance(object['Item'], list):
                    for i in object['Item']:
                        print(i['Properties'])
                else:
                    return {
                    "displayName" : [i['Value'] for i in object['Item']['Properties']['Item'] if i['Name']=='DisplayName'][0],
                    "principalName" : [i['Value'] for i in object['Item']['Properties']['Item'] if i['Name']=='UserPrincipalName'][0],
                    "status" : [i['Value'] for i in object['Item']['Properties']['Item'] if i['Name']=='Status'][0],
                    "mfaStatusCode" : [i['Value'] for i in object['Item']['Properties']['Item'] if i['Name']=='MfaStatusCode'][0],
                        }
            else:
                return {}
        else:
            return {}

    def query_all_users(self, skiptoken="", mfa_list = [], page=1):
        mfalist = mfa_list
        mfa_page = 'https://account.activedirectory.windowsazure.com/usermanagement/GenericFetchData.ajax'

        data = {
        "p0":"Microsoft.Online.BOX.Admin.UI.UserManagement.MultifactorVerification.FetchUsers",
        "p1":skiptoken,
        "p2":"{\"SortProperty\":\"\",\"SortOrder\":0}",
        "p3": page,
        "p4":"{\"FilterID\":\"db691acf-5f0c-4f1e-a9db-2a5b72665ded\",\"FilterType\":\"9\",\"SearchText\":\"\",\"MfaState\":\"Any\"}",
        "assembly":"BOX.UI, Version=2.0.0.0, Culture=neutral, PublicKeyToken=null",
        "class":"Microsoft.Online.BOX.UI.WebControls.ListGrid"
        }

        response = self._session.get(mfa_page, data=data, verify=True)
        if "SessionValid" in response.text:
            object = xmltodict.parse(response.text.strip("SessionValid"))['response']
            items = object["Items"]
            if items.get('Item'):
                if isinstance(items['Item'], list):
                    temp = []
                    for i in items['Item']:
                        id = i["ID"] 
                        for a in i["Properties"]["Item"]:
                            if a["Name"] == "DisplayName":
                                name = a["Value"]
                            elif a["Name"] == "UserPrincipalName":
                                principalName = a["Value"]
                            elif a["Name"] == "Status":
                                status = a["Value"]
                            elif a["Name"] == "MfaStatusCode":
                                statusCode = a["Value"]
                        temp.append({
                            "ID"                : id,
                            "Name"              : name,
                            "UserPrincipalName" : principalName,
                            "Status"            : status,
                            "MfaStatusCode"     : statusCode,
                            })
                    mfalist.extend(temp)
                    
                    dbgPrint.info(len(mfalist))
            page = object["Paging"]["NavigateDetails"]
            skiptoken = object["Paging"]["Context"]["ContextDetails"]
            self.query_all_users(skiptoken=skiptoken, mfa_list=mfalist, page=4)

        return mfalist
