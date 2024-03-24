import os
import argparse
import socket
import threading
from typing import List, Dict
from .requesthandlers import *
from .data import *


CODECRAFTERS = True

def codeCraftersGet(request,args):
    path = request.path
    resp = None
    if path.startswith("/echo/"):
        msg = request.path[6:] #strip off /echo/
        length = len(msg)
        headers = {
            "Content-Type": "text/plain"
        }
        resp = HTTPResponse(200, content=msg, **headers)
    elif path.startswith("/user-agent"):
        msg = request.headers.get("User-Agent")
        length = len(msg)
        headers = {
            "Content-Type": "text/plain"
        }
        resp = HTTPResponse(200,content=msg,**headers)
    elif path.startswith("/files/"):
        msg = request.path[6:] #strip /files
        _path = args.directory + msg
        if os.path.exists(_path):
            with open(_path,"r") as f:
                content = f.read()
            headers = {
                "Content-Type":"application/octet-stream"
            }
            resp = HTTPResponse(200,content=content,**headers)
    return resp

def codeCraftersPost(request, args):
    if request.path.startswith("/files"):
        msg = request.path[6:] #strip /files
        _path = args.directory + msg
        with open(_path,"w") as f:
            f.write(request.body)
        return HTTPResponse(201)

functiondict = {
    "GET": codeCraftersGet,
    "POST": codeCraftersPost
}

class HandlerThread:
    def __init__(self, conn, addr, args):
        self.thread = threading.Thread(
            target=self.handler, args=(conn, addr,args)
        ).start()
    
    def handler(self,conn, addr, requestHandler):
        with conn:
            data = conn.recv(1024).decode("utf-8")
            if data:
                req = HTTPRequest(data)
            try:
                resp = requestHandler.handleRequest(req)
            except Exception as e:
                resp = HTTPResponse(500, content=str(e))
            self.sendall(conn, resp)

    def sendall(self, conn, msg):
        if type(msg)!=HTTPResponse:
            raise ValueError("")
        print(msg)
        conn.sendall(repr(msg).encode("utf-8"))

def main(args):
    server_socket = socket.create_server(("localhost", 4221))#, reuse_port=True)
    requestHandler = HTTPRequestHandler(methods=["GET","POST"],args=args,codecraftersfns = functiondict)
    while True:
        conn, addr = server_socket.accept()
        HandlerThread(conn,addr,requestHandler)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--directory',nargs="?",default="./")
    args = parser.parse_args()
    if args.directory!=None:
        args.directory = args.directory[:-1] # remove last /
    main(args)
