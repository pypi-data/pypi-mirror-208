import os
import pickle as pkl
ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))

class ephemerisDecoder:
    """Class that decodes ephemeris specific messages, is called on by the sourceParser."""
    def __init__(self,GNSSDict,logger):
        """Initialize the ephemeris decoder with a dictionary of GNSS codes and our logger.
        """
        
        self.msg = None 
        self.GNSSDict = GNSSDict
        self.logger = logger
        
        #Initialization of header data 
        self.GNSS = None
        #Initialization of array that will store our data
        self.ephemerisData = [] 

    def setMsg(self,msg):
        self.msg = msg 
        self.ephemerisData = [] #Every time when changing message we clear the ephemeris data array
        self.GNSS = self.GNSSDict[int(self.msg.identity)]

    def decodeEphemeris(self):
        with open(os.path.join(ROOT_PATH,"utils","constants","dataFields.pkl"),"rb") as f:
            dataFields = pkl.load(f)[self.GNSS]
        try:
            [self.ephemerisData.append(getattr(self.msg,'DF'+str(i).zfill(3))) for i in dataFields["specific"]]
        except AttributeError:
            self.logger.warning("Attribute error for DF"+str(i).zfill(3) + " in "+self.GNSS+" ephemeris decoding")
            self.ephemerisData.append("NO DATA")
        for i in [x for x in range(dataFields["range"][0],dataFields["range"][1]) if x not in dataFields["exception"]]:
            try:
                self.ephemerisData.append(getattr(self.msg,'DF'+str(i).zfill(3)))
            except AttributeError:
                self.logger.warning("Attribute error for DF"+str(i).zfill(3) + " in "+self.GNSS+" ephemeris decoding")
                self.ephemerisData.append("NO DATA")