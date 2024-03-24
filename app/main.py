from dataclasses import dataclass, field
from typing import List, Dict
import os
import argparse
import socket
import threading

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
    pass

def codeCraftersResponse(request):
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
    return resp

class GetRequestHandler(RequestHandler):
    def __init__(self, args):
        self.args = args
    
    def handleRequest(self, request: HTTPRequest) -> Status:
        if request.method !="GET":
            raise ValueError("not a GET method")
        if request.path=="/":
            resp = HTTPResponse(200)
        elif CODECRAFTERS:
            resp = codeCraftersResponse(request)
        if resp == None:
            path = self.args.directory + request.path
            print(path)
            if os.path.exists(path):
                print("ok")
            try:
                headers = {"Content-Type":"application/octet-stream"}
                with open(path,"r") as f:
                    resp = HTTPResponse(200,content=f.read(),**headers)
            except Exception as e:
                print(e)
        if resp == None:
            resp = HTTPResponse(404)
        return resp

class HandlerThread:
    def __init__(self,handler, conn, addr,args):
        self.thread = threading.Thread(
            target=handler, args=(conn, addr,args)
        ).start()

def handler(conn, addr,args):
    getHandler = GetRequestHandler(args)
    with conn:
        data = conn.recv(1024).decode("utf-8")
        if data:
            req = HTTPRequest(data)
        try:
            resp = getHandler.handleRequest(req)
        except Exception as e:
            print(e)
            resp = HTTPResponse(500, content=str(e))
        conn_sendall(conn, resp)

def conn_sendall(conn, msg):
    conn.sendall(repr(msg).encode("utf-8"))

def main(args):
    server_socket = socket.create_server(("localhost", 4221))#, reuse_port=True)
    while True:
        conn, addr = server_socket.accept()
        HandlerThread(handler, conn,addr,args)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--directory',nargs="?",default="./")
    args = parser.parse_args()
    if args.directory!=None:
        args.directory = args.directory[:-1] # remove last /
    main(args)
