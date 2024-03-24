from dataclasses import dataclass, field
from typing import List
import socket

@dataclass
class HTTPRequest:
    request:str
    method: str = None
    path: str = None
    version: str = None
    headers: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        request = self.request.strip().split(b"\r\n")
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
        return f"HTTP/1.1 {self.code}\r\n"

class HTTPResponse:
    def __init__(self,status):
        self.status = Status(status)
    
    def __repr__(self):
        return f"{self.status}\r\n"

class RequestHandler:
    pass

class GetRequestHandler(RequestHandler):
    @classmethod
    def handleRequest(self, request: HTTPRequest) -> Status:
        if request.method !=b"GET":
            raise ValueError("not a GET method")
        print(request.path, request.path==b"/","*"*20)
        if request.path==b"/":
            return HTTPResponse(200)
        
        return HTTPResponse(404)

def conn_sendall(conn, msg):
    conn.sendall(repr(msg).encode("utf-8"))

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 4221))#, reuse_port=True)
    conn, addr = server_socket.accept()
    with conn:
        print(f"Connected from {addr}")
        data = conn.recv(1024)
        if data:
            req = HTTPRequest(data)
        try:
            response = GetRequestHandler.handleRequest(req)
        except:
            response = HTTPResponse(500)
        conn_sendall(conn, response)


if __name__ == "__main__":
    main()
