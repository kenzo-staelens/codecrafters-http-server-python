from dataclasses import dataclass, field, KW_ONLY
from typing import List, Dict
import os
import argparse
import socket
import threading

CODECRAFTERS = True
RESPONSECODES = {
    200: "OK",
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
        request = self.request.strip().split("\r\n")
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
    def __new__(cls, args):
        instance = super().__new__(cls)
        instance.args = args
        instance.method = None
        return instance
    
    def handleRequest(self, request: HTTPRequest) -> Status:
        if request.method !=self.method:
            raise ValueError("not a GET method")
        return self._handleRequest(request)

@dataclass
class HTTPRequestHandler:
    methods: List[str] = None
    _: KW_ONLY
    args: argparse.Namespace = field(default_factory=argparse.Namespace)
    handlers: Dict[str,RequestHandler] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.methods == None:
            self.methods = ["GET"]
        if "GET" in self.methods:
            self.handlers["GET"]=GetRequestHandler(self.args)
        if "POST" in self.methods:
            self.handlers["POST"]=PostRequestHandler(self.args)
    
    def handleRequest(self, request: HTTPRequest) -> Status:
        handler = self.handlers.get(request.method)
        if handler:
            return handler.handleRequest(request)
        return HTTPResponse(415)

class GetRequestHandler(RequestHandler):
    def __init__(self,args):
        self.method = "GET"
    
    def _handleRequest(self, request: HTTPRequest) -> Status:
        if request.path=="/":
            resp = HTTPResponse(200)
        elif CODECRAFTERS:
            resp = codeCraftersGet(request,self.args)
        
        if resp == None:
            resp = HTTPResponse(404)
        return resp

class PostRequestHandler(RequestHandler):
    def __init__(self,args):
        self.method = "POST"
    
    def _handleRequest(self, request: HTTPRequest) -> Status:
        pass

def codeCraftersPost(request, args):
    pass

def codeCraftersGet(request,args):
    path = request.path
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
    elif path.startswith("/files/"):
        msg = request.path[6:] #strip /files
        _path = args.directory + request.path.strip("/files")
        print(_path)
        if os.path.exists(_path):
            headers = {"Content-Type":"application/octet-stream"}
            with open(_path,"r") as f:
                resp = HTTPResponse(200,content=f.read(),**headers)
    return resp

class HandlerThread:
    def __init__(self,handler, conn, addr,args):
        self.thread = threading.Thread(
            target=handler, args=(conn, addr,args)
        ).start()

def handler(conn, addr,requestHandler):
    with conn:
        data = conn.recv(1024).decode("utf-8")
        if data:
            req = HTTPRequest(data)
        try:
            resp = requestHandler.handleRequest(req)
        except Exception as e:
            print(e)
            resp = HTTPResponse(500, content=str(e))
        conn_sendall(conn, resp)

def conn_sendall(conn, msg):
    if type(msg)!=HTTPResponse:
        raise ValueError("")
    conn.sendall(repr(msg).encode("utf-8"))

def main(args):
    server_socket = socket.create_server(("localhost", 4221))#, reuse_port=True)
    requestHandler = HTTPRequestHandler(methods=["GET","POST"],args=args)
    while True:
        conn, addr = server_socket.accept()
        HandlerThread(handler, conn,addr,requestHandler)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--directory',nargs="?",default="./")
    args = parser.parse_args()
    if args.directory!=None:
        args.directory = args.directory[:-1] # remove last /
    main(args)
