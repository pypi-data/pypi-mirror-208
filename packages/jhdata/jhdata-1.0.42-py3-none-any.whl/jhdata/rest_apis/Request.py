import requests

from jhdata.rest_apis.RequestParameters import RequestParameters


class Request:
    """
    HTTP Request Class

    Represents a HTTP request
    """

    def __init__(self, table: str, name: str, **kwargs):
        """
        Constructor

        table: str  ->  Name of table this request loads data for
        name: str   ->  Name of the request
        kwargs      ->  Any named parameters. The ones compatible with requests.request are added
                        to the RequestParameters object
        """
        self.table = table
        self.name = name

        self.request_parameters = RequestParameters(**kwargs)

        self.response = None
        self.data = None

    def __setattr__(self, key, value):
        """If available
        """
        if hasattr(self.request_parameters, key):
            setattr(self.request_parameters, key, value)
        else:
            self.__dict__[key] = value

    def __getattr__(self, key):
        if hasattr(self.request_parameters, key):
            return getattr(self.request_parameters, key)
        else:
            return self.__dict__[key]

    def execute(self):
        self.response = requests.request(**self.request_parameters.dict)
        self.data = self.response

        return self
