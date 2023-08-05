from dataclasses import dataclass, asdict
from typing import Union, List, Any, Dict


@dataclass
class RequestParameters:
    url: str = None
    method: str = "GET"
    params: Union[dict, List[tuple], bytes] = None
    data: Union[dict, List[tuple], bytes] = None
    json: Dict[str, Any] = None
    headers: Dict[str, str] = None
    cookies: Dict = None
    files: Dict[str, Any] = None
    auth: tuple = None
    timeout: Union[float, tuple] = None
    allow_redirects: bool = None
    proxies: Dict[str, str] = None
    verify: bool = None
    stream: bool = None
    cert: Union[str, tuple] = None

    @property
    def dict(self):
        return {k: v for k, v in asdict(self).items()}

    def copy(self):
        return RequestParameters(**self.dict())
