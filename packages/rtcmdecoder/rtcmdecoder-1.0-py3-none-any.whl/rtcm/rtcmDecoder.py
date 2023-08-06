import threading
import collections

import rtcm.utils.argumentParser as ap
import rtcm.dataProcessing.sourceParser as sp
import rtcm.dataProcessing.CSVWriter as csvw
import rtcm.clients.ntripClient as ntrip
import rtcm.clients.receiverClient as rc

def rtcmdecoder():
    """Main function of the RTCM decoder. It parses the arguments, initializes the logger, and starts the threads.
    Can be seen as the central controller of the program."""
    global terminateSignal
    args, logger = ap.argumentParser()
    print("""        
                                            :!JJ~.              
                    ^7!!^^~^.          :!?5B&&&#P?:            
                    :Y!~^~7?J?~.    :~7YG###BB###&&&P~          
                    .!^^^^:^~7?7~..~YPB##BBB####&#GY!:          
                    .?!^^^^!?PBPBP?: ^YGB##&&&B5?^.             
                    ^??~~JBG5B#&GP7.. ^5BBPY!:                 
                .. :J55BPG&#J77?J7!!7^^^.                    
                :~7JJ?!::!Y##Y7?7?Y5YY?7^.                      
        .:~7JY555PGY^   ~PJ~?55YY555YJ7~:                    
    .:~7JYYY55PPP555G5^^~7YY??55555Y5PGGY!                   
    ^?JY55555PYY55PG#&&B5!.  ~J?7Y555G#&@@#~   .:::::.         
    :?555555YY5PG#&#GJ!:.     .!J7?P#@@@@@@7^777?77?P!         
    7YYYY5GB&#GY7^.           :7?P#&&&&BPJ?J?7777!!.         
        ~5GB#BP?~.                 :~~~~J5J?JJY5P5PY^           
        ~PJ!:                         ~?77Y55555Y!.            
                                    !JJY5PP55J7!              
                                    :YPPPPPY7^..!!             
                                    .5P5Y?~.     .             
                                    .:.                       
    _________________________________________________________""")
    csvWriter = csvw.CSVWriter(args.inputType,args.mode,args.output,args.filesize,logger)
    csvWriter.initializeCSV()
    try:
        match args.inputType:
            case "file":
                parser = sp.sourceParser(args.mode,args.input,logger)
                parser.decodeFile()
                csvWriter.writeFileCSV(parser)
                return
            case "stream":
                client = rc.receiverClient(args.baudrate,logger)
            case "server":
                client = ntrip.ntripClient(args.server,args.mountpoint,args.username,args.password,args.port,logger)
                args.password = '\x00'*len(args.password) # Clear password from memory
            case _:
                logger.error("Invalid input type, program only supports file, stream and server")
                raise ValueError("Invalid input type")
        try:
            client.connect()
        except ConnectionError:
            logger.error("Failed to connect")
            logger.error("Exiting")
            raise ConnectionError("Failed to connect") 
        parser = sp.sourceParser(args.mode,client.conn,logger)
        myBuffer = collections.deque()
        terminateSignal = threading.Event()
        threads = [threading.Thread(target=parser.decodeLive,args=(args.listening,myBuffer,terminateSignal)),
                threading.Thread(target=csvWriter.writeLiveCSV,args=(myBuffer,terminateSignal))]
        for thread in threads:
            thread.daemon = True
            thread.start()
        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        print("Exiting program…\n")
        try:
            terminateSignal.set()
        except InterruptedError:
            logger.error("Failed to terminate threads, closer inspection needed")
            exit()
        
if __name__ == '__main__':
    rtcmdecoder()