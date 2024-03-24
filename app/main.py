import socket

class Status:
    def __init__(self, code):
        self.code = code
    
    def __repr__(self):
        return f"HTTP/1.1 {self.code}\r\n"

class HTTPResponse:
    def __init__(self,status):
        self.status = Status(status)
    
    def __repr__(self):
        return f"{self.status}\r\n"

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
            pass
        conn_sendall(conn, HTTPResponse(200))


if __name__ == "__main__":
    main()
