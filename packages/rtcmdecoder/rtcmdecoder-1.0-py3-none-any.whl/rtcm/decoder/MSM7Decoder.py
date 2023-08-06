import numpy as np

global c
c = 299_792_458 #Meters per second, global variable, defined on page 207

class MSM7Decoder:
    """Class to decode MSM7 messages."""
    def __init__(self,MSM7Dict,logger):
        
        #Initialization of the logger 
        self.logger = logger
                
        #Initialization of the dictionary with the GNSS identifiers
        self.MSM7Dict = MSM7Dict
        
        #Initialization of the raw message
        self.msg = None 
        
        #Initialization of variables we need to calculate/recover form our messages -- End values 
        self.GNSS = None 
        self.PRN = None 
        self.epoch = None 
        self.pseudorange = None 
        self.phaserange = None 
        self.phaserangeRate = None 
        self.CNR = None 
        
        #Header data
        self.satsUsed = None
        self.satsUsedTot = None 
        self.NSat = None 
        self.NSigTot = None
        self.rinexCode = None 
        
        
        #Satellite data field
        self.Nms = None
        self.roughRange = None
        self.roughPhaseRangeRate  = None

        #Signal data 
        self.finePseudoRange = None 
        self.finePhaseRange = None 
        self.lockTime = None
        self.lockTimeIndicator = None
        self.finePhaseRangeRate = None 

        self.MSM7Data = []

        
    #Standard getters and setters
    def setMsg(self,msg):
        self.msg = msg
        
    #Decoding functions 
    def decodeHeader(self):
        #0. Which GNSS 
        self.GNSS = self.MSM7Dict[int(self.msg.identity)]
        #1. Decoding the satMask 
        satMask = (bin(self.msg.DF394)[2:]).zfill(64) #Gives us a string with which satellites we have 
        satsUsed = []
        for ind,val in enumerate(satMask):
            if val == '1':
                satsUsed.append(ind+1)
        self.satsUsed = satsUsed
        self.NSat = len(satsUsed)
        self.epoch = self.msg.GNSSEpoch
        
        #2.Decoding signal mask 
        sigMask = bin(self.msg.DF395)[2:].zfill(32) #Gives us a string with which signals we have
        sigsUsed = []
        for ind,val in enumerate(sigMask):
            if val == '1':
                sigsUsed.append(ind+1)
        NSig = len(sigsUsed)
        
        cellMask = bin(self.msg.DF396)[2:].zfill(self.NSat*NSig)
        realSatsUsed = []
        rinexCode = []
        #Decoding cell mask to get the number of signals sent per satellite!
        for i in range(self.NSat*NSig):
            j = i//NSig
            k = i%NSig
            if cellMask[i] == '1':
                realSatsUsed.append(satsUsed[j])
                rinexCode.append(sigsUsed[k])
        self.satsUsedTot = realSatsUsed
        self.NSigTot = len(realSatsUsed)
        self.rinexCode = rinexCode
        
    def decodeSatelliteData(self):
        satelliteSecs = []
        satelliteRough = []
        satelliteRoughPhase = [] 
        for i in range(self.NSat):
            num = str(i+1).zfill(2)
            satelliteSecs.append(getattr(self.msg,'DF397_'+num))
            satelliteRough.append(getattr(self.msg,'DF398_'+num))
            satelliteRoughPhase.append(getattr(self.msg,'DF399_'+num))
        self.Nms = dict(zip(self.satsUsed,satelliteSecs)) 
        self.roughRange = dict(zip(self.satsUsed,satelliteRough))
        self.roughPhaseRangeRate= dict(zip(self.satsUsed,satelliteRoughPhase))
        
    def decodeSignalData(self):
        finePseudo = np.zeros((self.NSigTot,1))
        finePhase = np.zeros((self.NSigTot,1))
        lockTime =np.zeros((self.NSigTot,1))
        satCNR = np.zeros((self.NSigTot,1))
        finePhaseRate = np.zeros((self.NSigTot,1))
        for i in range(self.NSigTot):
            num = str(i+1).zfill(2)
            finePseudo[i] = getattr(self.msg,'DF405_'+num)
            finePhase[i] = getattr(self.msg,'DF406_'+num)
            lockTime[i] = getattr(self.msg,'DF407_'+num)
            valCNR = getattr(self.msg,'DF408_'+num)
            valFinePhaseRate = getattr(self.msg,'DF404_'+num)
            if valCNR == 0:
                self.logger.warning("Invalid value for CNR, setting to None")
                valCNR = None #If value is zero, it means that the CNR is not available
            satCNR[i] = valCNR
            if valFinePhaseRate == -1.6834:
                self.logger.warning("Invalid value for fine phase range rate, setting to None")
                valFinePhaseRate = None #Page 93 of documentation rtcm, invalid value! -->Manual inspection needed
            finePhaseRate[i] = valFinePhaseRate
        self.finePseudoRange = finePseudo
        self.finePhaseRange = finePhase
        self.lockTime = lockTime
        self.CNR = satCNR
        self.finePhaseRangeRate = finePhaseRate  


    def getRangeData(self):
        pseudo = np.zeros((self.NSigTot,1))
        phaseRange = np.zeros((self.NSigTot,1))
        phaseRangeRate = np.zeros((self.NSigTot,1))
        for i in range(self.NSigTot):
            pseudo[i] = (c/1000 * (self.Nms[self.satsUsedTot[i]] + self.roughRange[self.satsUsedTot[i]]/1024 + (2**-29) * self.finePseudoRange[i]))
            phaseRange[i] = (c/1000 * (self.Nms[self.satsUsedTot[i]] + self.roughRange[self.satsUsedTot[i]]/1024 + (2**-31) * self.finePhaseRange[i]))
            phaseRangeRate[i] = (self.roughPhaseRangeRate[self.satsUsedTot[i]] + 0.0001*self.finePhaseRangeRate[i])
        self.pseudorange = pseudo
        self.phaserange = phaseRange
        self.phaserangeRate = phaseRangeRate

    def getLockTimeIndicator(self):
        lockTimeIndicator = np.zeros((self.NSigTot,1))
        #p220, rewritten as a function to avoid having 23 if statements
        for i in range(self.NSigTot):
            if self.lockTime[i][0] < 2**6:
                lockTimeIndicator[i] = self.lockTime[i][0]
            elif self.lockTime[i] > 2**26:
                lockTimeIndicator[i] = 704
            else:
                for power in range(7,26):
                    if self.lockTime[i][0] < 2**power:
                        lockTimeIndicator[i] = (2**6+(power-7)*32) + (self.lockTime[i][0]-2**(power-1))/(2**(power-6))
                        break
        self.lockTimeIndicator = lockTimeIndicator


    def decodeMSM7(self):
        self.decodeHeader()
        self.decodeSatelliteData()
        self.decodeSignalData()
        self.getRangeData()
        self.getLockTimeIndicator()
        self.MSM7Data = [[self.GNSS, str(self.satsUsedTot[i]).zfill(2), self.rinexCode[i], self.epoch, self.pseudorange[i][0], self.phaserange[i][0], self.phaserangeRate[i][0], self.CNR[i][0], self.lockTimeIndicator[i][0]] for i in range(self.NSigTot)]