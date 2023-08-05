"""
Secret Interfaces are meant to be a flexible way of pulling secrets from different places,
e.g. a dict in memory, environment variables, Airflow variables, Azure Key Vault...
"""


class SecretInterface:
    def __init__(self, getter=lambda key: None, setter=lambda key, value: None):
        self.getter = getter
        self.setter = setter

    def get(self, key, default=None):
        secret = self.getter(key)
        return secret if secret is not None else default

    def set(self, key, value):
        self.setter(key, value)

    def list(self):
        return []

    def substitute(self, original_string: str):
        substituted_string = original_string

        for key in self.list():
            substituted_string = substituted_string.replace('$' + key, self.get(key))

        return substituted_string


class SecretInterfaceMemory(SecretInterface):
    def __init__(self, secrets=None):
        self.secrets = secrets if secrets is not None else {}
        super().__init__()

    def get(self, key, default=None):
        return self.secrets[key] if key in self.secrets else default

    def set(self, key, value):
        self.secrets[key] = value

    def list(self):
        return self.secrets.keys()


"""
Collection of Secret Interfaces.
When get() is called, tries to pull the value from the Interfaces one by one until a hit is found
set() sets the value for all Interfaces
"""
class SecretInterfaceCollection(SecretInterface):
    def __init__(self, interfaces):
        super().__init__()
        self.interfaces = interfaces

    def get(self, key, default=None):
        for interface in self.interfaces:
            secret = interface.get(key)
            if secret is not None:
                return secret

        return default

    def set(self, key, value):
        for interface in self.interfaces:
            interface.set(key, value)

    def list(self):
        keys = []

        for interface in self.interfaces:
            keys += interface.list()

        return list(set(keys))
