from dataclasses import dataclass, field
from typing import List, Dict
import socket

CODECRAFTERS = True
RESPONSECODES = {
    200: "OK",
    404: "NOT FOUND",
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
        request = self.request.strip().split(b"\r\n")
        request = [x.decode("utf-8") for x in request]
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
        headers = [f"\r\n{k}: {v}" for k,v in self.headers.items()]
        headers = "".join(headers)
        return f"{self.status}{headers}\r\n\r\n{self.content}"

class RequestHandler:
    pass

def codeCraftersResponse(request):
    path = request.path
    print(request)
    resp = None
    if path.startswith("/echo/"):
        msg = request.path[6:] #strip off /echo/
        length = len(msg)
        headers = {
            "Content-Type": "text/plain",
            "Content-Length": str(length)
        }
        resp = HTTPResponse(200, content=msg, **headers)
    elif path.startswith("/user-agent"):
        msg = request.headers.get("User-Agent")
        length = len(msg)
        headers = {
            "Content-Type": "text/plain",
            "Content-Length": str(length)
        }
        resp = HTTPResponse(200,content=msg,**headers)
    return resp

class GetRequestHandler(RequestHandler):
    @classmethod
    def handleRequest(self, request: HTTPRequest) -> Status:
        if request.method !="GET":
            raise ValueError("not a GET method")
        if request.path=="/":
            resp = HTTPResponse(200)
        if CODECRAFTERS:
            resp = codeCraftersResponse(request)
        if resp==None:
            resp = HTTPResponse(404)
        return resp

def conn_sendall(conn, msg):
    conn.sendall(repr(msg).encode("utf-8"))

def main():
    server_socket = socket.create_server(("localhost", 4221))#, reuse_port=True)
    conn, addr = server_socket.accept()
    with conn:
        data = conn.recv(1024)
        if data:
            req = HTTPRequest(data)
        try:
            response = GetRequestHandler.handleRequest(req)
        except Exception as e:
            response = HTTPResponse(500, content=str(e))
        conn_sendall(conn, response)

if __name__ == "__main__":
    main()
