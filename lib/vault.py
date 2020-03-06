import hvac
import requests

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

    def get_total_leases(self):
        pass

        leases_lookup = requests.request('LIST', 
                self.addr + "/v1/sys/leases/lookup",
                headers={'X-Vault-Token': self.token, 'X-Vault-Namespace': "root/"}
            ).json()

        accesors = requests.request('LIST', 
                self.addr + "/v1/sys/leases/lookup/auth/token/create",
                headers={'X-Vault-Token': self.token, 'X-Vault-Namespace': "root/"}
            ).json()


        
