import socket 
import base64 

class ntripClient:
    def __init__(self,host,mountpoint,username,password,port,logger):
        """Connection to NTRIP server and sends authorization credentials

        Args:
            host (string): The IP (or URL) of the NTRIP server you want to connect to
            port (int): The port number of the NTRIP server you want to connect to (default: 2101)
            mountpoint (str): The mountpoint in the NTRIP server you want to connect to
            username (str): Your username to the NTRIP server
            password (str, optional): Your password to the NTRIP server. Defaults to "None".
            port (int, optional): The port you want to connect to. Defaults to 2101.
            
        Returns:
            NtripClient: An NtripClient object
        """
        self.logger = logger

        # Encode username and password in base64 for transmission
        self.host = host
        self.port = port
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        auth_str = f"{username}:{password}".encode('utf-8')
        auth_b64 = base64.b64encode(auth_str).decode('utf-8')

        # Construct GET request with mountpoint and authorization headers
        request = f"GET /{mountpoint} HTTP/1.1\r\n"
        request += f"Host: {self.host}\r\n"
        request += "Ntrip-Version: Ntrip/1.0\r\n"
        request += "User-Agent: NTRIP Python Client\r\n"
        request += "Connection: close\r\n"
        request += f"Authorization: Basic {auth_b64}\r\n"
        request += "\r\n"
        self.request = request

    def connect(self):
        # Open socket connection to NTRIP server and send request
        self.logger.info("Attempting to connect")
        self.conn.settimeout(5) 
        self.conn.connect((self.host, self.port))
        self.conn.settimeout(None)
        self.conn.send(self.request.encode('utf-8'))
        # Receive response from server
        response = self.conn.recv(4096*2) 
        self.logger.info("Connected")
        self.logger.info(response.decode('utf-8'))