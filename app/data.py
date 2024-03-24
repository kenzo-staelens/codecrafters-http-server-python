from dataclasses import dataclass, field, KW_ONLY
from typing import List, Dict

RESPONSECODES = {
    200: "OK",
    201: "CREATED",
    404: "NOT FOUND",
    415: "METHOD NOT ALLOWED",
    500: "INTERNAL SERVER ERROR"
}

@dataclass
class HTTPRequest:
    request:str
    method: str = field(init=False)
    path: str = field(init=False)
    version: str = field(init=False)
    headers: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        try:
            request,body = self.request.strip().split("\r\n"*2)
            self.body = body
        except:
            request = self.request.strip()
            self.body = ""
        request = request.split("\r\n")
        self.request = request[0]
        requestline = request[0].split()
        self.method = requestline[0]
        self.path = requestline[1]
        self.version = requestline[1]
        self.headers = {(kv:=request.split(": "))[0]:kv[1] for request in request[1:]}

@dataclass
class Status:
    code: int
    
    def __repr__(self):
        return f"HTTP/1.1 {self.code} {RESPONSECODES[self.code]}"


class HTTPResponse:
    def __init__(self, status, *, content="", **headers):
        self.status: Status = Status(status)
        self.content: str = content
        self.headers: Dict[str, str] = headers
        
    def __repr__(self):
        self.headers |= {"Content-Length":len(self.content)}
        headers = [f"\r\n{k}: {v}" for k,v in self.headers.items()]
        headers = "".join(headers)
        return f"{self.status}{headers}\r\n\r\n{self.content}"