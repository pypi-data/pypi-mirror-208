import os
import time

from pyrtcm import RTCMReader
import pickle as pkl 
import rtcm.decoder.MSM7Decoder as msm7
import rtcm.decoder.ephemerisDecoder as eph
import alive_progress as ap

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))


class sourceParser:
    """Secondary controller of the system, it is called on by the main controller and it calls on the decoders."""
    def __init__(self,mode,input,logger):
        self.mode = mode 
        self.input = input
        self.outputMSM7 = []
        self.outputEphemeris = {
            "GPS":[],
            "GLONASS":[],
            "IRNSS":[],
            "BDS":[],
            "QZSS":[],
            "Galileo F/NAV":[],
            "Galileo I/NAV":[]
        }
        self.timeRunOut = float('inf')
        self.connectionTime = time.time()
        self.logger = logger 
        self.logger.info("Source parser initialized")

    def decodeFile(self):
        self.logger.info("Reading file")
        inputBytes = open(self.input,'rb')
        self.logger.info("File read")
        rtr = RTCMReader(inputBytes)
        testRtr = rtr
        if testRtr.read() == (None,None):
            self.logger.error("Invalid file type inserted")
            raise TypeError("Invalid file type")
        self.logger.info("File read and parsed")
        self.decoder(rtr)

    def decodeLive(self,timeRunOut,buffer,terminateSignal):
        self.timeRunOut = timeRunOut
        self.logger.info("Parsing bytes")
        rtr = RTCMReader(self.input)
        self.logger.info("Bytes parsed")
        self.decoder(rtr,buffer,terminateSignal)
        self.logger.info("Closing connection")
        self.input.close()
        terminateSignal.set()

    def decoder(self,rtr,buffer=None,terminateSignal=None):
        self.logger.info(str(self.mode)+" mode selected")
        with open(os.path.join(ROOT_PATH,"utils","constants","GNSSCodes.pkl"),"rb") as f:
            MSM7Dict = pkl.load(f)["MSM7"]
        with open(os.path.join(ROOT_PATH,"utils","constants","GNSSCodes.pkl"),"rb") as f:
            ephemerisDict = pkl.load(f)["Ephemeris"]
        self.logger.info("GNSS codes loaded for decoding")
        decoderMSM7 = msm7.MSM7Decoder(MSM7Dict,self.logger)
        decoderEphemeris = eph.ephemerisDecoder(ephemerisDict,self.logger)
        self.logger.info("Starting decoding")

        with ap.alive_bar() as bar:
            for (_,parsed_data) in rtr:
                bar()
                if int(parsed_data.identity) in MSM7Dict.keys() and self.mode != "ephemeris":
                    decoderMSM7.setMsg(parsed_data)
                    decoderMSM7.decodeMSM7()
                    [self.outputMSM7.append(data) for data in decoderMSM7.MSM7Data]
                if int(parsed_data.identity) in ephemerisDict.keys() and self.mode != "MSM7":
                    decoderEphemeris.setMsg(parsed_data)
                    decoderEphemeris.decodeEphemeris()
                    self.outputEphemeris[ephemerisDict[int(parsed_data.identity)]].append(decoderEphemeris.ephemerisData)
                if buffer is not  None:
                    buffer.appendleft([self.outputMSM7,self.outputEphemeris])
                    #reset back to default in case of buffer, otherwise it will append the whole live session to self.outputXXX
                    self.outputMSM7 = []
                    self.outputEphemeris = {
                        "GPS":[],
                        "GLONASS":[],
                        "IRNSS":[],
                        "BDS":[],
                        "QZSS":[],
                        "Galileo F/NAV":[],
                        "Galileo I/NAV":[]
                    }
                    if time.time() - self.connectionTime > self.timeRunOut:
                        self.logger.info("Timelimit reached")
                        terminateSignal.set()
                        break
        self.logger.info("Decoding done")