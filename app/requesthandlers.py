from typing import List, Dict, Callable
from data import *
import argparse

class RequestHandler:
    def __new__(cls, args, codecraftersfn=None):
        instance = super().__new__(cls)
        instance.args = args
        instance.codecraftersfn = codecraftersfn
        instance.method = None
        return instance
    
    def handleRequest(self, request: HTTPRequest) -> Status:
        if request.method !=self.method:
            raise ValueError("not a GET method")
        return self._handleRequest(request)

class GetRequestHandler(RequestHandler):
    def __init__(self,args,codecraftersfn):
        self.method = "GET"
    
    def _handleRequest(self, request: HTTPRequest) -> Status:
        if request.path=="/":
            resp = HTTPResponse(200)
        elif self.codecraftersfn!=None:
            resp = self.codecraftersfn(request,self.args)
        
        if resp == None:
            resp = HTTPResponse(404)
        return resp

class PostRequestHandler(RequestHandler):
    def __init__(self,args,codecraftersfn):
        self.method = "POST"
    
    def _handleRequest(self, request: HTTPRequest) -> Status:
        if self.codecraftersfn!=None:
            return self.codecraftersfn(request,self.args)

methodHandlers = {
    "GET":GetRequestHandler,
    "POST":PostRequestHandler
}

@dataclass
class HTTPRequestHandler:
    methods: List[str] = None
    _: KW_ONLY
    args: argparse.Namespace = field(default_factory=argparse.Namespace)
    handlers: Dict[str,RequestHandler] = field(default_factory=dict)
    codecraftersfns: Dict[str,Callable] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.methods == None:
            self.methods = ["GET"]
        for method in self.methods:
            self.handlers[method]=methodHandlers[method](self.args, self.codecraftersfns[method])
    
    def handleRequest(self, request: HTTPRequest) -> Status:
        handler = self.handlers.get(request.method)
        if handler:
            return handler.handleRequest(request)
        return HTTPResponse(415)