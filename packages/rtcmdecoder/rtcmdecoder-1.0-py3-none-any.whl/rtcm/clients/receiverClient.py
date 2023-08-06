from serial import Serial, SerialException
from serial.tools import list_ports

class receiverClient: 
    def __init__(self,baudrate,logger):
        self.port = None
        self.baudrate= baudrate
        self.logger = logger
        self.conn = None
    
    def identifyPorts(self):
        """ Lists serial port names

            :raises EnvironmentError:
                On unsupported or unknown platforms
            :returns:
                A list of the serial ports available on the system
        """
        allPorts = list_ports.comports()
        if len(allPorts) == 0: 
            self.logger.error("No ports found on your device, compatibility issue")
            raise ConnectionError
        USBPorts = []
        for port, desc, hwid in sorted(allPorts):
            if "USB" in hwid:
                self.logger.info("{}: {} [{}]".format(port, desc, hwid))
                USBPorts.append(port)
                
        result = []

        for port in USBPorts:
            try:
                conn = Serial(port)
                conn.close()
                result.append(port)
            except (OSError, SerialException):
                pass
        return result
        
    def connect(self):
        possPorts = self.identifyPorts()
        for port in possPorts:
            stream = Serial(port,baudrate=self.baudrate,timeout=1)
            if stream.isOpen() and stream.read(64) != b'':
                self.logger.info(f"Connected to {port}")
                self.conn = stream
                return 
        self.logger.error("No USB ports found to connect to")
        raise ConnectionError