import requests
from utils.logger import logger

class ZabbixService:
    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password
        self.headers = {'Content-Type': 'application/json-rpc'}
        
    def _call_api(self, method, params, auth=None):
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1
        }
        if auth:
            payload["auth"] = auth
            
        try:
            response = requests.post(self.url, headers=self.headers, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            if 'error' in data:
                logger.error(f"Zabbix API Error on {method}: {data['error']}")
                raise Exception(f"API Error: {data['error'].get('data', 'Unknown error')}")
            return data.get('result')
        except Exception as e:
            logger.error(f"Failed to call Zabbix API: {str(e)}")
            raise e

    def login(self):
        logger.info(f"Authenticating with Zabbix API as {self.username}")
        params = {"user": self.username, "password": self.password}
        result = self._call_api("user.login", params)
        if result:
            return result
        raise Exception("Failed to retrieve auth token")
        
    def logout(self, auth_token):
        logger.info("Logging out from Zabbix API")
        self._call_api("user.logout", [], auth=auth_token)

    def get_user_groups(self, auth_token):
        logger.info("Fetching user groups from Zabbix")
        params = {
            "output": ["usrgrpid", "name"],
            "sortfield": "name"
        }
        return self._call_api("usergroup.get", params, auth=auth_token)

    def check_user_exists(self, auth_token, alias):
        logger.info(f"Checking if user '{alias}' already exists")
        params = {
            "output": ["userid", "alias"],
            "filter": {
                "alias": [alias]
            }
        }
        result = self._call_api("user.get", params, auth=auth_token)
        return len(result) > 0

    def create_user(self, auth_token, alias, name, surname, roleid, usrgrpids, passwd):
        logger.info(f"Creating user '{alias}' with type {roleid}")
        usrgrps = [{"usrgrpid": str(grp_id)} for grp_id in usrgrpids]
        
        params = {
            "alias": alias,
            "name": name,
            "surname": surname,
            "passwd": passwd,
            "type": int(roleid),
            "usrgrps": usrgrps
        }
        result = self._call_api("user.create", params, auth=auth_token)
        logger.info(f"User created successfully: {result}")
        return result
