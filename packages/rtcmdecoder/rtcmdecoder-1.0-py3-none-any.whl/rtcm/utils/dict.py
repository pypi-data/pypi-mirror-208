import pickle as pkl

sigIDGPS = {
    2: ["L1", "C/A","1C"],
    3: ["L1", "P", "1P"],
    4: ["L1","Z-tracking or similar","1W"],
    8: ["L2","C/A","2C"],
    9: ["L2","P","2P"],
    10: ["L2","Z-tracking or similar","2W"],
    15: ["L2","L2C(M)","2S"],
    16: ["L2","L2C(L)","2L"],
    17: ["L2","L2C(M+L)","2X"],
    22: ["L5","I","5I"],
    23: ["L5","Q","5Q"],
    24: ["L5","I+Q","5X"],
    30: ["L1","L1C-D","1S"],
    31: ["L1","L1C-P","1L"],
    32: ["L1","L1C(D+P)","1X"],
}

sigIdBeidou = {
    2: ["B1","I","2I"],
    3: ["B1","Q","2Q"],
    4: ["B1","I+Q","2X"],
    8: ["B3","I","6I"],
    9: ["B3","Q","6Q"],
    10: ["B3","I+Q","6X"],
    14: ["B2","I","7I"],
    15: ["B2","q","7Q"],
    16: ["B2","I+Q","7X"],
    22: ["B2a","D","5D"],
    23: ["B2a","P","5P"],
    24: ["B2a","D+P","5X"],
    25: ["B2b","I","7D"],
    30: ["B1C","D","1D"],
    31: ["B1C","P","1P"],
    32: ["B1C","D+P","1X"]  
}

sigIdGLONASS = {
    2: ["G1", "C/A", "1C"],
    3: ["G1", "P", "1P"],
    8: ["G2", "C/A", "2C"],
    9: ["G2", "P", "2P"]
}

sigIdGalileo = {
    2: ["E1", "C no data", "1C"],
    3: ["E1", "A", "1A"],
    4: ["E1", "BI/NAV OS/CS/SoL", "1B"],
    5: ["E1", "B+C", "1X"],
    6: ["E1", "A+B+C", "1Z"],
    8: ["E6", "C", "6C"],
    9: ["E6", "A", "6A"],
    10: ["E6", "B", "6B"],
    11: ["E6", "B+C", "6X"],
    12: ["E6", "A+B+C", "6Z"],
    14: ["E5B", "I", "7I"],
    15: ["E5B", "Q", "7Q"],
    16: ["E5B", "I+Q", "7X"],
    18: ["E5(A+B)", "I", "8I"],
    19: ["E5(A+B)", "Q", "8Q"],
    20: ["E5(A+B)", "I+Q", "8X"],
    22: ["E5A", "I", "5I"],
    23: ["E5A", "Q", "5Q"],
    24: ["E5A", "I+Q", "5X"]
} 

SBASDict = {
    2: ["L1", "C/A", "1C"],
    22: ["L5", "I", "5I"],
    23: ["L5", "Q", "5Q"],
    24: ["L5", "I+Q", "5X"]
}

QZSSDict = {
    2: ["L1", "C/A", "1C"],
    9: ["LEX", "S", "6S"],
    10: ["LEX", "L", "6L"],
    11: ["LEX", "S+L", "6X"],
    15: ["L2", "L2C(M)", "2S"],
    16: ["L2", "L2C(L)", "2L"],
    17: ["L2", "L2C(M+L)", "2X"],
    22: ["L5", "I", "5I"],
    23: ["L5", "Q", "5Q"],
    24: ["L5", "I+Q", "5X"],
    30: ["L1", "L1C(D)", "1S"],
    31: ["L1", "L1C(P)", "1L"],
    32: ["L1", "L1C(D+P)", "1X"]
}

IRNSSDict = {
    8: ["S", "SPS-S", "9A"],
    22: ["L5", "SPS-L5", "5A"]
}

MSM7Dict = {
    1077:"GPS", 
    1087:"GLONASS",
    1097:"Galileo",
    1107:"SBAS",
    1117:"QZSS",
    1127:"BeiDou",
    1137:"IRNSS",
}

ephemerisDict = {
    1019:"GPS",
    1020:"GLONASS",
    1041:"IRNSS",
    1042:"BDS",
    1044:"QZSS",
    1045:"Galileo F/NAV",
    1046:"Galileo I/NAV",
}

GNSSCodesDict = {
    "MSM7": MSM7Dict,
    "Ephemeris": ephemerisDict
}

sigIDDict = {
    "GPS": sigIDGPS,
    "Beidou": sigIdBeidou,
    "GLONASS": sigIdGLONASS,
    "Galileo": sigIdGalileo,
    "SBAS": SBASDict,
    "QZSS": QZSSDict,
    "IRNSS": sigIdGLONASS
}

MSM7Header = ["GNSS","Satellite ID","RINEX","Epoch","Pseudorange [m]","Phaserange [m]","Phaserange rate [m/s]","CNR [DB-Hz]","Lock Time Indicator"]

ephemerisHeaderDict = {
    "GPS":["Satellite ID","IODE","Fit Interval","Week Number","SV Accuracy","Code on L2","IDOT","t_oc","a_f2","a_f1","a_f0","IODC","C_rs","DELTA n","M_0","C_uc","e","C_us","A^1/2","t_oe","C_ic","OMEGA_0","C_is","i_0","C_rc","omega","OMEGADOT","t_gd","SV HEALTH","L2 P data flag"],
    
    "GLONASS":["Satellite ID","Satellite Frequency Channel Number","Almanac Health","Almanac Health availability indicator","P1","t_k","MSb of B_n word","P2","t_b","x_n(t_b),first derivative","x_n(t_b)","x_n(t_b),second derivative","y_n(t_b),first derivative","y_n(t_b)","y_n(t_b),second derivative","z_n(t_b),first derivative","z_n(t_b)","z_n(t_b),second derivative","P3","gamma_n(t_b)","GLONASS-M P","GLONASS-M l_n (third string)","tau_n(t_b)","GLONASS-M DELTA tau_n","E_n","GLONASS-M P4","GLONASS-M F_T","GLONASS-M N_T","GLONASS-M M","Availability of additional data","N^A","tau_c","GLONASS-M N_4","GLONASS-M tau_GPS","GLONASS-M l_n (fifth string)"],
    
    "Galileo F/NAV":["Satellite ID","Week Number","IODnav","SV SISA","IDOT","t_oc","a_f2","a_f1","a_f0","C_rs","DELTA n","M_0","C_uc","e","C_us","A^1/2","t_oe","C_ic","OMEGA_0","C_is","i_0","C_rc","omega","OMEGADOT","BGD_E5a/E1","NAV signal health status", "NAV data vaildity status"],
    
    "Galileo I/NAV":["Satellite ID","Week Number","IODnav","SISA Index (E1,E5b)","IDOT","t_oc","a_f2","a_f1","a_f0","C_rs","DELTA n","M_0","C_uc","e","C_us","A^1/2","t_oe","C_ic","OMEGA_0","C_is","i_0","Crc","omega","OMEGADOT","BGDE5a/E1","BGDE5b/E1","E5b Signal Health Status","E5b Data Validity Status","E1-B Signal Health Status","E1-B Data Validity Status"],
    
    "QZSS":["Satellite ID", "t_oc", "a_f2", "a_f1", "a_f0", "IODE", "C_rs", "DELTA n_0", "M_0", "C_uc", "e", "C_us", "A^1/2", "t_oe", "C_ic", "OMEGA_0", "C_is", "i_0", "C_rc", "omega_n", "OMEGADOT", "IDOT", "Code on L2 Channel", "Week Number", "URA", "SV Health", "T_GD", "IODC", "Fit Interval"],
    
    "BDS":["Satellite ID", "Week Number", "SV URAI", "IDOT", "AODE", "t_oc", "a_2", "a_1", "a_0", "AODC", "C_rs", "DELTA n", "M_0", "C_uc", "e", "C_us", "A^1/2", "t_oe", "C_ic", "OMEGA_0", "C_is", "i_0", "C_rc", "omega", "OMEGADOT", "T_GD1", "T_GD 2", "SV Health"],
    
    "IRNSS":["Satellite ID", "Week Number", "a_f0", "a_f1","a_f2", "SV Accuracy", "t_oc", "T_GD", "DELTA n", "IODEC", "Reserved bits after IODEC", "L5 Flag", "S Flag", "C_uc","C_us", "C_ic", "C_is", "C_rc", "C_rs", "IDOT", "M_0", "t_oe","e","A^1/2", "OMEGA_0", " omega", "OMEGADOT", "i_0", "Spare bits after IDOT","Spare bits after i_0"],
}

CSVHeaderDict = {
    "MSM7":MSM7Header,
    "ephemeris":ephemerisHeaderDict
}

GPSFields = {
    "specific":[9,71,137],
    "range":[76,104],
    "exception":[80]
}

GLONASSFields = {
    "specific":[38,40],
    "range":[104,137],
    "exception":[]
}

GalileoFNAVFields = {
    "specific":[252],
    "range":[289,316],
    "exception":[313]
}

GalileoINAVFields = {
    "specific":[252],
    "range":[286,318],
    "exception":[291,314,315]
}

QZSSFields = {
    "specific":[],
    "range":[429,458],
    "exception":[]
}

BDSFields = {
    "specific":[],
    "range":[488,516],
    "exception":[]
}

IRNSSFields = {
    "specific":[],
    "range":[516,547],
    "exception":[]
}

dataFields = {
    "GPS":GPSFields,
    "GLONASS":GLONASSFields,
    "Galileo F/NAV":GalileoFNAVFields,
    "Galileo I/NAV":GalileoINAVFields,
    "QZSS":QZSSFields,
    "BDS":BDSFields,
    "IRNSS":IRNSSFields
}

with open("constants/sigID.pkl", "wb") as f:
    pkl.dump(sigIDDict,f)
    
with open("constants/GNSSCodes.pkl", "wb") as f:
    pkl.dump(GNSSCodesDict,f)

with open("constants/CSVHeaders.pkl", "wb") as f:
    pkl.dump(CSVHeaderDict,f)

with open("constants/dataFields.pkl", "wb") as f:
    pkl.dump(dataFields,f)