import hvac
import requests

class Vault:
    def __init__(self, addr, token):
        self.token = token
        self.addr = addr
        self.client = hvac.Client(addr, token)

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
    
    def get_auth_methods(self):
        return self.client.sys.list_auth_methods()['data']

    def is_initialized(self):
        return self.client.is_initialized()
    
    def get_policies(self):
        return self.client.sys.list_policies()['data']['policies']
    
    def get_list_namespaces(self):
        return self.client.sys.list_namespaces()
    
    def get_secrets_engine_list(self):
        return self.client.sys.list_mounted_secrets_engines()['data']

    def uptime(self):
        return "We need to improve this"

    def get_metricts(self):
        return requests.get(
            self.addr + "/v1/sys/metrics?format=", 
            headers={'X-Vault-Token': self.token}
        ).json()

    def get_expire_leases(self):
        return requests.get(
            self.addr + "/v1/sys/leases", 
            headers={'X-Vault-Token': self.token}
        ).json()

    def get_configuration(self):
        return requests.get(
            self.addr + "/v1/sys/config/state", 
            headers={'X-Vault-Token': self.token}
        ).json()

    def get_health(self):
        return requests.get(
            self.addr + "/v1/sys/health", 
            headers={'X-Vault-Token': self.token}
        ).json()

    def get_general_information(self):
        return requests.get(
            self.addr + "/v1/sys/host-info", 
            headers={'X-Vault-Token': self.token}
        ).json()

    def get_version(self):
        return requests.get(
            self.addr + "/v1/sys/health", 
            headers={'X-Vault-Token': self.token}
        ).json()['version']

    def get_features(self):
        return requests.get(
            self.addr + "/v1/sys/license", 
            headers={'X-Vault-Token': self.token}
        ).json()

    def get_integrated_apps(self):
        return requests.get(
            self.addr + "/v1/sys/mounts", 
            headers={'X-Vault-Token': self.token}
        ).json()

    def wrapping(self, function):
        return requests.get(
            self.addr + "/v1/sys/wrapping/" + function, 
            headers={'X-Vault-Token': self.token}
        ).json()
