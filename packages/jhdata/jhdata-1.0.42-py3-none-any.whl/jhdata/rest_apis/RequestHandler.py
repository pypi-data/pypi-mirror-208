from concurrent.futures import ThreadPoolExecutor, wait

from jhdata.rest_apis.Request import Request
from jhdata.rest_apis.RequestParameters import RequestParameters


class RequestHandler:
    """Helper Class to handle HTTP requests"""

    def __init__(self, parallel_workers=10):
        """
        Constructor

        parallel_workers: int -> Number of operations to run in parallel
        """
        self.requests = []
        self.defaults = RequestParameters()
        self.parallel_workers = parallel_workers

    def add(self, request: Request):
        """Add a request"""
        self.requests.append(request)
        return self

    def execute(self):
        """Execute all requests"""
        return self.transform(lambda request: request.execute())

    def transform(self, function, timeout=None):
        """
        Apply a transformation to all requests

        function: Transformation to be applied to each requests data
        timeout: Timeout for the overall transformation. Is passed to the ThreadPool
        """
        futures = []

        with ThreadPoolExecutor(max_workers=1) as executor:
            for request in self.requests:
                futures.append(executor.submit(function, request))

        wait(futures, timeout)
        return self
