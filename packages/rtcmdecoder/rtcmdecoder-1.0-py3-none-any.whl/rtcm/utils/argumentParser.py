import argparse
from sys import argv
import logging

def argumentParser():
    """Parses the arguments passed to the program and returns the parsed arguments and a logger object."""
    formatter = lambda prog: argparse.HelpFormatter(prog,max_help_position=52,indent_increment=2)
    parser = argparse.ArgumentParser(
        prog = "rtcmdecoder",
        description="Decoder for various types of RTCM messages",
        formatter_class=formatter)    
    
    fileInput = parser.add_argument_group('File input')
    serverInput = parser.add_argument_group("Server input")
    streamInput = parser.add_argument_group("Stream input")

    parser.add_argument("-d","--debug",help="Debug mode", action="store_true")
    parser.add_argument("-it","--inputType",metavar='\b',help="Type of input. Currently file, stream and server are supported.", required=True,type=str)
    parser.add_argument("-m","--mode",metavar='\b', help="Mode of operation. Currently MSM7, ephemeris and both are supported. Default to both", required=False,default="both",type=str)
    parser.add_argument("-o","--output",metavar='\b', help="Output directory. Will overwrite previous sessions.", required=True,type=str)

    fileInput.add_argument("-i","--input",metavar='\b', help="Input file", required=("file" in argv),type=str)

    serverInput.add_argument("-s","--server",metavar='\b', help="Server address", required=("server" in argv),type=str)
    serverInput.add_argument("-p","--port",metavar='\b', help="Server port", required=("server" in argv),type=int)
    serverInput.add_argument("-u","--username",metavar='\b', help="Username", required=("server" in argv),type=str)
    serverInput.add_argument("-pw","--password",metavar='\b', help="Password", required=("server" in argv),type=str)
    serverInput.add_argument("-mp","--mountpoint",metavar='\b', help="Mountpoint", required=("server" in argv),type=str)
    lt = serverInput.add_argument("-lt","--listening",metavar='\b', help="Listening time in minutes", required=False,default=float('inf'),type=float)
    fs = serverInput.add_argument("-fs","--filesize",metavar='\b', help="Maximal output filesize in MB", required=False,default=None,type=float)

    streamInput.add_argument("-bd","--baudrate",metavar='\b', help="Baudrate", required=("stream" in argv),type=int)
    streamInput._group_actions.append(lt)
    streamInput._group_actions.append(fs)
    
    #Set up logging
    parentLogger = logging.getLogger('parent')
    parentLogger.setLevel(logging.WARNING)

    childLogger = logging.getLogger('parent.child')
    childLogger.propagate = False

    handler = logging.StreamHandler()
    handler.setLevel(logging.WARNING)
    handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S'))

    parentLogger.addHandler(handler)
    childLogger.addHandler(handler)


    args = parser.parse_args()
    
    if args.inputType not in ["file","server","stream"]:
        raise ValueError("Invalid input type. Valid types are file, server and stream.")
    elif args.mode not in ["MSM7","ephemeris","both"]:
        raise ValueError("Invalid mode. Valid modes are MSM7, ephemeris and both.") 
    

    if args.debug:
        parentLogger.setLevel(logging.INFO)
        handler.setLevel(logging.INFO)
    args.listening *= 60 #converting to seconds
    if args.filesize:
        args.filesize *= 10**6 #converting to bytes
        
    return args, childLogger