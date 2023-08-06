import os
import time

import pandas as pd
import pickle as pkl

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))

class CSVWriter:
    """Class that writes data to CSV files, is called on by the sourceParser."""
    def __init__(self,inputType,mode,directory,fileSize,logger):
        self.inputType = inputType
        self.mode = mode
        self.outputDirectory = directory
        self.fileSize = fileSize
        self.logger = logger
        self.headersFile = "CSVHeaders.pkl"
        if not os.path.exists(self.outputDirectory):
            os.makedirs(self.outputDirectory)
        
    def initializeCSV(self):
        with open(os.path.join(ROOT_PATH,"utils","constants",self.headersFile),"rb") as f:
            MSM7Header = pkl.load(f)["MSM7"]
        outputPath = os.path.join(self.outputDirectory,"MSM7.csv")
        pd.DataFrame(columns=MSM7Header).to_csv(outputPath, encoding='utf-8',header=True,mode='w',index=False)
        with open(os.path.join(ROOT_PATH,"utils","constants",self.headersFile),"rb") as f:
            ephemerisHeaderDict = pkl.load(f)["ephemeris"]
        for GNSS in ephemerisHeaderDict.keys():
            outputPath = os.path.join(self.outputDirectory,"ephemeris"+GNSS.replace("/","").replace(" ","")+".csv")
            pd.DataFrame(columns=ephemerisHeaderDict[GNSS]).to_csv(outputPath, encoding='utf-8',header=True,mode='w',index=False)

    def writeMSM7(self,newRows):
        with open(os.path.join(ROOT_PATH,"utils","constants",self.headersFile),"rb") as f:
            MSM7Header = pkl.load(f)["MSM7"]
        outputPath = os.path.join(self.outputDirectory,"MSM7.csv")
        pd.DataFrame(newRows,columns=MSM7Header).to_csv(outputPath, encoding='utf-8',mode='a',header=False,index=False)

    def writeEphemeris(self,newRows):
        with open(os.path.join(ROOT_PATH,"utils","constants",self.headersFile),"rb") as f:
            ephemerisHeaderDict = pkl.load(f)["ephemeris"]
        for GNSS in ephemerisHeaderDict.keys():
            outputPath = os.path.join(self.outputDirectory,"ephemeris"+GNSS.replace("/","").replace(" ","")+".csv")
            pd.DataFrame(newRows[GNSS],columns=ephemerisHeaderDict[GNSS]).to_csv(outputPath, encoding='utf-8',mode='a',header=False,index=False)

    def shortenFile(self,fileName):
        outputPath = os.path.join(self.outputDirectory,fileName.replace("/","").replace(" ","")+".csv")
        with open(outputPath,"r") as f:
            lines = f.readlines()
            size = os.path.getsize(outputPath)
            linesToRemove = len(lines)-round(self.fileSize/size*len(lines)/1.25)
            if self.fileSize < size:
                with open(outputPath,"w") as out:
                    out.writelines(lines[0])
                    out.writelines(lines[linesToRemove:])

    def circularBuffer(self):
        if self.mode != "ephemeris":
            self.shortenFile("MSM7")
        elif self.mode != "MSM7":
            with open(os.path.join(ROOT_PATH,"utils","constants",self.headersFile),"rb") as f:
                ephemerisHeaderDict = pkl.load(f)["ephemeris"]
            fileNames = ["ephemeris"+GNSS for GNSS in ephemerisHeaderDict.keys()]
            for file in fileNames:
                self.shortenFile(file)

    def writeFileCSV(self,newRows):
        self.logger.info("Writing to file")
        match self.mode:
            case "MSM7":
                self.writeMSM7(newRows.outputMSM7)
            case "ephemeris":
                self.writeEphemeris(newRows.outputEphemeris)
            case "both":
                self.writeMSM7(newRows.outputMSM7)
                self.writeEphemeris(newRows.outputEphemeris)

    def writeLiveCSV(self,buffer,terminateSignal):
        self.logger.info("Writing to files")
        initialTime = time.time()
        while not terminateSignal.is_set() or buffer:
            try:
                newRows = buffer.pop()
            except IndexError:
                continue
            else:
                match self.mode:
                    case "MSM7":
                        self.writeMSM7(newRows[0])
                    case "ephemeris":
                        self.writeEphemeris(newRows[1])
                    case "both":
                        self.writeMSM7(newRows[0])
                        self.writeEphemeris(newRows[1])
            if self.fileSize and (time.time() - initialTime)%30 > 27:
                self.circularBuffer()