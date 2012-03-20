"""
    Module for generating attacker parameter
    Each entry in the file is a different type of attacker
        
    Asssumptions: For now we assume that attacker will have only searching sesssions
    So count for other session types will be only 1 & P will be 3600
"""
import string
import datetime
import time
import pyparsing
import argparse
import os, sys
import re
import random
import datetime
import time
from argparse import ArgumentParser, ArgumentTypeError
def parseRange(string):
    rangelist = string.split('-')
    if not rangelist or len(rangelist) !=2:
        raise ArgumentTypeError("Invalid range format")
    try:
        rangelist[0]=str(rangelist[0])
        rangelist[1]=str(rangelist[1])
    except:
        raise ValueError('Number in '+string+' is not integer')
    return [rangelist[0],rangelist[1]]

# parse commandline arguments
def parseCmdArgs():
    desc = "flash crowd attack generation tool"
    parser = argparse.ArgumentParser(description=desc,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                add_help=False)
    parser.add_argument("-h", "--help", action="help",
            help="Show this help message and exit")
    parser.add_argument("-o", "--outfile", default=None,
            help="File to dump attackers parameters")
    parser.add_argument("-n", "--num-attacker", type=int, required = True,
            help="Number of attacker to generate")
    parser.add_argument("-N", "--num-session-range", type=parseRange, 
            default=[10,100],
            help="specify the min & max number of sessions")
    parser.add_argument("-P", "--pause-range", type=parseRange, 
            default=[10,60],
            help="specify the min & max session pause")
    parser.add_argument("-r", "--num-request-range", type=parseRange, 
            default=[5,50],
            help="specify the min & max number of request")
    parser.add_argument("-a", "--gap-range", type=parseRange, 
            default=[0.02,0.1],
            help="specify the min & max gap")
    parser.add_argument("-N2", "--num2-session-range", type=parseRange, 
            default=[10,100],
            help="specify the min & max number of s2 sessions")
    parser.add_argument("-P2", "--pause2-range", type=parseRange, 
            default=[10,60],
            help="specify the min & max s2 session pause")
    parser.add_argument("-N3", "--num3-session-range", type=parseRange, 
            default=[10,100],
            help="specify the min & max number of s3 sessions")
    parser.add_argument("-P3", "--pause3-range", type=parseRange, 
            default=[10,60],
            help="specify the min & max s3 session pause")
    parser.add_argument("-N4", "--num4-session-range", type=parseRange, 
            default=[10,100],
            help="specify the min & max number of s4 sessions")
    parser.add_argument("-P4", "--pause4-range", type=parseRange, 
            default=[10,60],
            help="specify the min & max s4 session pause")
    args = parser.parse_args()
    return args
def setAttackerAddress(attacker_address):
    if attacker_address[3] < 255:
        attacker_address[3]+=1
    elif attacker_address[2] < 255:
        attacker_address[2]+=1
        attacker_address[3]=0
    elif attacker_address[1] < 255:
        attacker_address[1]+=1
        attacker_address[2]=0
    elif attacker_address[0] < 11:
        attacker_address[0]+=1
        attacker_address[1]=0
    else:
        print "Maximum Number of attackers 10*255*255*255 limit reached"
        return None
    return attacker_address

def getNPraForOthers(N,P,r,a):
    browsingSes= []
    relaxedSes = []
    longSes = []
    """
    since attacker consist of only searching session, so
    N_other =1 for other session types
    P_other = 3600 for other session types
    """
    N_other =1
    P_other = 3600
    R = int(N * r) 
    r_other = R/N_other
    a_other = float(N*(r-1)*a +(N-1)*P)/(N*(r-1)+(N-1))
    """
    Don't add R in the parameter list so that it won't be used in trainig
    return [N_other,P_other,r_other,a_other,N_other,P_other,r_other,a_other,\
                N_other,P_other,r_other,a_other,R]
    """
    return [N_other,P_other,r_other,a_other,N_other,P_other,r_other,a_other,\
                N_other,P_other,r_other,a_other]



#parse commandlist arguments    
args = parseCmdArgs()
outputStream = None
try:
    outputStream = open(args.outfile,"w")
except:
    # happend when the outfile is specified incorrectly 
    # or not specified at all
    outputStream = sys.stdout

#num session range
min_session=int(args.num_session_range[0])
max_session=int(args.num_session_range[1])
#session pause range
min_pause=float(args.pause_range[0])
max_pause=float(args.pause_range[1])
#num of request range
min_req =float(args.num_request_range[0])
max_req =float(args.num_request_range[1])
#gap range
min_gap=float(args.gap_range[0])
max_gap=float(args.gap_range[1])
#num s2 session range
minN2=int(args.num2_session_range[0])
maxN2=int(args.num2_session_range[1])
#s2 session pause range
minP2=float(args.pause2_range[0])
maxP2=float(args.pause2_range[1])
#num s3 session range
minN3=int(args.num3_session_range[0])
maxN3=int(args.num3_session_range[1])
#s3 session pause range
minP3=float(args.pause3_range[0])
maxP3=float(args.pause3_range[1])
#num s4 session range
minN4=int(args.num4_session_range[0])
maxN4=int(args.num4_session_range[1])
#s4 session pause range
minP4=float(args.pause4_range[0])
maxP4=float(args.pause4_range[1])

attacker_count = 0
N_values = []
P_values = []
r_values = []
a_values = []
N2_values = []
P2_values = []
N3_values = []
P3_values = []
N4_values = []
P4_values = []
while attacker_count < args.num_attacker:
    N = int(random.uniform(min_session,max_session))
    P = random.uniform(min_pause,max_pause)
    r = random.uniform(min_req,max_req)
    a = random.uniform(min_gap,max_gap)
    N2 = int(random.uniform(minN2,maxN2))
    P2 = random.uniform(minP2,maxP2)
    N3 = int(random.uniform(minN3,maxN3))
    P3 = random.uniform(minP3,maxP3)
    N4 = int(random.uniform(minN4,maxN4))
    P4 = random.uniform(minP4,maxP4)
    
    N_values.append(N)
    P_values.append(P)
    r_values.append(r)
    a_values.append(a)
    N2_values.append(N2)
    P2_values.append(P2)
    N3_values.append(N3)
    P3_values.append(P3)
    N4_values.append(N4)
    P4_values.append(P4)

    attacker_count+=1

N_values = sorted(N_values,reverse=True)
P_values = sorted(P_values)
r_values = sorted(r_values,reverse=True)
a_values = sorted(a_values)
N2_values = sorted(N2_values,reverse=True)
P2_values = sorted(P2_values)
N3_values = sorted(N3_values,reverse=True)
P3_values = sorted(P3_values)
N4_values = sorted(N4_values,reverse=True)
P4_values = sorted(P4_values)

i = 0
while i < args.num_attacker:
    N = N_values[i]
    P = P_values[i]
    r = r_values[i]
    a = a_values[i]
    N2 = N2_values[i]
    P2 = P2_values[i]
    N3 = N3_values[i]
    P3 = P3_values[i]
    N4 = N4_values[i]
    P4 = P4_values[i]

    searchingSession = [N,P,r,a]
    """
    # get NPra for other sesssions types
    NPra_Others = getNPraForOthers(N,P,r,a)
    """
    """
    for 10 parameters
    """
    NPra_Others = [N2,P2,N3,P3,N4,P4]

    """
    for all 10 parameters
    """
    parameters = searchingSession
    parameters.extend(NPra_Others)
    """
    for only searching session parameters
    """
    #parameters = searchingSession
    #write the parameters
    # convert list to comma seperated string
    outputString = ",".join([str(round(x,2)) for x in parameters])
    outputString += ",ATTACKER\n" 
    outputStream.write(outputString)
    i+=1

