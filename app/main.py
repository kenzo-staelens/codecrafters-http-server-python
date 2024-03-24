from dataclasses import dataclass, field
from typing import List
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
        self.headers = request[1:]

@dataclass
class Status:
    code: int
    
    def __repr__(self):
        return f"HTTP/1.1 {self.code} {RESPONSECODES[self.code]}"

@dataclass
class HTTPResponse:
    status: Status
    headers: List[str] = field(default_factory=list)
    content: str = field(default_factory=str)
    
    def __post_init__(self):
        self.status = Status(self.status)
    
    def __repr__(self):
        headers = "".join(["\r\n"+header for header in self.headers])
        return f"{self.status}{headers}\r\n\r\n{self.content}"

class RequestHandler:
    pass

def codeCraftersResponse(request):
    msg = request.path[6:] #strip off /echo/
    length = len(msg)
    headers = [
        "Content-Type: text/plain",
        f"Content-Length: {length}"
        ]
    resp = HTTPResponse(200, headers, content=msg)
    print(resp)
    return resp

class GetRequestHandler(RequestHandler):
    @classmethod
    def handleRequest(self, request: HTTPRequest) -> Status:
        if request.method !="GET":
            raise ValueError("not a GET method")
        if request.path==b"/":
            return HTTPResponse(200)
        if CODECRAFTERS:
            return codeCraftersResponse(request)
        
        return HTTPResponse(404)

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
