from datetime import datetime
import hvac
import requests
import json

class Vault:
    def __init__(self, addr, token):
        self.token = token
        self.addr = addr
        self.client = hvac.Client(addr, token)

    # General
    def cleanup_json(self, data):
        cleaned = dict()
        for k,v in data.items():
            if v is None or v == '':
                print(k,v)
                continue

            cleaned[k] = v
        return cleaned

    def query_vault(self, path):
        url = self.addr + path
        return self.cleanup_json(requests.get(
            url,
            headers={'X-Vault-Token': self.token, 'X-Vault-Namespace': "root/"}
        ).json())

    
    # HVAC General Functions
    def is_authenticated(self):
        return self.client.is_authenticated()

    def get_status(self):
        if not self.is_authenticated():
            return None

        return self.client.sys.read_health_status(method='GET')

    def is_root(self):
        data = self.client.lookup_token()['data']
        path = data['path']
        policies = data['policies']
        return path == 'auth/token/root' or 'root' in policies

    def get_identity(self):
        return self.client.lookup_token()['data']

    def get_audit_devices(self):
        return self.client.sys.list_enabled_audit_devices()['data']

    def is_initialized(self):
        return self.client.is_initialized()

    def get_policies(self):
        return self.client.sys.list_policies()['data']['policies']

    def get_metricts(self):
        return self.query_vault("/v1/sys/metrics?format=")

    def get_expire_leases(self):
        return self.query_vault("/v1/sys/leases")

    def get_configuration(self):
        return self.query_vault("/v1/sys/config/state/sanitized")

    def get_health(self):
        return self.query_vault("/v1/sys/health")

    def get_general_information(self):
        return self.query_vault("/v1/sys/host-info")

    def get_version(self):
        return self.query_vault("/v1/sys/health")['version']

    def get_features(self):
        return self.query_vault("/v1/sys/license")

    def get_integrated_apps(self):
        return self.query_vault("/v1/sys/mounts")

    def wrapping(self, function):
        return self.query_vault("/v1/sys/wrapping/" + function)

    def get_roles(self):
        return self.query_vault("/v1/auth/token/roles")


    # Adoption Stat 1 Functions
    def get_overall_month(self):
        file_content = open('vault_audit.log')
        file_content = file_content.readlines()

        arr_moths = {}

        for line in file_content:
            json_line = json.loads(line)
            time = json_line['time'].split("T")[0]
            datetime_object = datetime.strptime(time, '%Y-%m-%d')
            month = datetime_object.month
            
            if arr_moths.get(month, False):
                arr_moths[month] += 1
            else:
                arr_moths[month] = 1

        today_month = datetime.today().month

        if arr_moths.get(today_month, 0) > arr_moths.get(today_month - 1, 0):
            return "Positive :arrow_up:"
        else:
            return "Negative :arrow_down:"

    def get_overall_week(self):
        file_content = open('vault_audit.log')
        file_content = file_content.readlines()

        arr_days = {}

        for line in file_content:
            json_line = json.loads(line)
            time = json_line['time'].split("T")[0]
            datetime_object = datetime.strptime(time, '%Y-%m-%d')
            day = datetime_object.day
            
            if datetime.today().month == datetime_object.month:
                if arr_days.get(day, False):
                    arr_days[day] += 1
                else:
                    arr_days[day] = 1

        today_day = datetime.today().day

        if arr_days.get(today_day, 0) > arr_days.get(today_day - 1, 0):
            return "Positive :arrow_up:"
        else:
            return "Negative :arrow_down:"

    def vault_operations(self):
        file_content = open('vault_audit.log')
        file_content = file_content.readlines()

        arr_moths = {}

        for line in file_content:
            json_line = json.loads(line)
            time = json_line['time'].split("T")[0]
            datetime_object = datetime.strptime(time, '%Y-%m-%d')
            month = datetime_object.month
            
            if arr_moths.get(month, False):
                arr_moths[month] += 1
            else:
                arr_moths[month] = 1

        today_month = datetime.today().month
        return arr_moths.get(today_month, 0)

    def get_secrets_engine_list(self):
        return self.client.sys.list_mounted_secrets_engines()['data'].keys()
    
    def get_auth_methods(self):
        return self.client.sys.list_auth_methods()['data']
    
    # Adoption Stat 2 Functions 
    def get_total_entities_count(self):
        return requests.request('LIST', 
                self.addr + "/v1/identity/entity/id",
                headers={'X-Vault-Token': self.token, 'X-Vault-Namespace': "root/"}
            ).json().get('data', {})

    def get_total_roles(self):
        total_roles = 0
        
        mount_keys = requests.get(self.addr + "/v1/sys/auth",
                headers={'X-Vault-Token': self.token, 'X-Vault-Namespace': "root/"}
            ).json()['data'].keys()

        mounts = [k for k in mount_keys]

        for mount in mounts:
            plain_users = requests.request('LIST', 
                self.addr + "/sys/auth" + mount + "/users",
                headers={'X-Vault-Token': self.token, 'X-Vault-Namespace': "root/"}
            ).json().get('data', {}).get('keys', [])

            users = len(plain_users)

            print("*************", users, flush=True)

            plain_roles = requests.request('LIST', 
                self.addr + "/sys/auth" + mount + "/roles",
                headers={'X-Vault-Token': self.token, 'X-Vault-Namespace': "root/"}
            ).json().get('data', {}).get('keys', [])

            roles = len(plain_roles)

            print("+++++++++++++", roles, flush=True)
            
            total_roles = total_roles + users + roles

        return total_roles

    def get_total_tokens(self):
        total_tokens = 0

        accesor_keys = requests.request('LIST', 
                self.addr + "/v1/auth/token/accessors",
                headers={'X-Vault-Token': self.token, 'X-Vault-Namespace': "root/"}
            ).json().get('data', {}).get('keys', [])

        total_tokens = len(accesor_keys)

        return total_tokens

    def get_change_percentage(self):
        file_content = open('vault_audit.log')
        file_content = file_content.readlines()

        total = len(file_content)
        arr_days = {}

        for line in file_content:
            json_line = json.loads(line)
            time = json_line['time'].split("T")[0]
            datetime_object = datetime.strptime(time, '%Y-%m-%d')
            day = datetime_object.day
            
            if datetime.today().month == datetime_object.month:
                if arr_days.get(day, False):
                    arr_days[day] += 1
                else:
                    arr_days[day] = 1

        today_day = datetime.today().day

        operations_change = arr_days.get(today_day, 0)
        
        change_percentage = divmod((operations_change * 100), total)[0]

        return str(change_percentage) + "%"

    # Extant Leases Functions
    def get_total_leases(self):

        token_accessors = requests.request('LIST', 
                self.addr + "/v1/sys/leases/lookup/auth/token/create",
                headers={'X-Vault-Token': self.token}
            ).json()

        accesor_array = token_accessors.get('data', {}).get('keys', [])

        total_leases = len(accesor_array)

        return total_leases


    def get_leases_detail(self):
        longest_ttl = None
        shortest_ttl = None
        longest = None
        shortest = None
        renewable = 0
        non_renewable = 0
        infinite_ttl = 0
        
        token_accessors = requests.request('LIST', 
                self.addr + "/v1/sys/leases/lookup/auth/token/create",
                headers={'X-Vault-Token': self.token}
            ).json()

        accesor_array = token_accessors.get('data', {}).get('keys', [])

        for accesor in accesor_array:
            
            lease_id = "auth/token/create/" + accesor
            put_data = "{\"lease_id\": \"auth/token/create/" + accesor + "\"}"
            
            lease_info = requests.request('PUT', 
                self.addr + "/v1/sys/leases/lookup",
                headers={'X-Vault-Token': self.token},
                data=put_data
            ).json()

            expire_time = lease_info.get('data', {}).get('expire_time', False)
            is_renewable = lease_info.get('data', {}).get('renewable', False)
            lease_ttl = lease_info.get('data', {}).get('ttl', False)

            if longest_ttl == None:
                longest_ttl = lease_ttl
                longest = expire_time
            else:
                if longest_ttl < lease_ttl:
                    longest_ttl = lease_ttl
                    longest = expire_time
            

            if shortest_ttl == None:
                if lease_ttl > 0:
                    shortest_ttl = lease_ttl
                    shortest = expire_time
            else:
                if shortest_ttl > lease_ttl and lease_ttl > 0:
                    shortest_ttl = lease_ttl
                    shortest = expire_time

            if is_renewable:
                renewable += 1
            else:
                non_renewable += 1

            if lease_ttl == 0:
                infinite_ttl += 1

        # Formating dates 2020-03-09T20:13:17.838583701Z
        if shortest is not None:
            short = shortest.split("T")
            time = short[1].split(".")[0]
            date_time_short = short[0] + " " + time
        else:
            date_time_short = ""

        if longest is not None:
            long_t = longest.split("T")
            time = long_t[1].split(".")[0]
            date_time_long = long_t[0] + " " + time
        else:
            date_time_long = ""

        detail_data = { "longest": date_time_long, 
                        "shortest": date_time_short, 
                        "shortest_ttl": shortest_ttl,
                        "longest_ttl": longest_ttl,
                        "renewable": renewable, 
                        "non_renewable": non_renewable,
                        "infinite_ttl": infinite_ttl
                      }

        return detail_data

        '''
            Lease data
            {'request_id': '30439b26-762a-629e-4b1f-35c35c2ea1e7', 'lease_id': '', 
            'renewable': False, 'lease_duration': 0, 
            'data': {'expire_time': None, 'id': 'auth/token/create/e3bf69abeea8f32f00111f17128fa5e5a25d6b07', 
            'issue_time': '2020-03-09T18:53:14.609577415Z', 
            'last_renewal': None, 'renewable': False, 'ttl': 0}, 
            'wrap_info': None, 'warnings': None, 'auth': None}
        '''
