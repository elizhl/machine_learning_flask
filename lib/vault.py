import hvac

class Vault:
    def __init__(self, addr, token):
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
    
    # def disable_auth_method(self):
    #     return self.client.lookup_token()['data']
    
    # def revoke_token(self):
    #     return self.client.lookup_token()['data']
    
    # def read_secret(self):
    #     return self.client.lookup_token()['data']