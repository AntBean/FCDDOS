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
    totNumReq = int(N * r) 
    r_other = totNumReq/N_other
    a_other = float(N*(r-1)*a +(N-1)*P)/(N*(r-1)+(N-1))
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
max_session=int(args.num_session_range[1])+1
#session pause range
min_pause=float(args.pause_range[0])
max_pause=float(args.pause_range[1])
#num of request range
min_req =float(args.num_request_range[0])
max_req =float(args.num_request_range[1])
#gap range
min_gap=float(args.gap_range[0])
max_gap=float(args.gap_range[1])
attacker_count = 0
N_values = []
P_values = []
r_values = []
a_values = []
while attacker_count < args.num_attacker:
    N = int(random.uniform(min_session,max_session))
    P = random.uniform(min_pause,max_pause)
    r = random.uniform(min_req,max_req)
    a = random.uniform(min_gap,max_gap)
    N_values.append(N)
    P_values.append(P)
    r_values.append(r)
    a_values.append(a)

    attacker_count+=1
N_values = sorted(N_values,reverse=True)
P_values = sorted(P_values)
r_values = sorted(r_values,reverse=True)
a_values = sorted(a_values)

i = 0
while i < args.num_attacker:
    N = N_values[i]
    P = P_values[i]
    r = r_values[i]
    a = a_values[i]
    searchingSession = [N,P,r,a]
    # get NPra for other sesssions types
    NPra_Others = getNPraForOthers(N,P,r,a)
    #get the N,P,r,a for browsing, relaxed, long session
    parameters = searchingSession
    parameters.extend(NPra_Others)
    #write the parameters
    # convert list to comma seperated string
    outputString = ",".join([str(round(x,1)) for x in parameters])
    outputString += ",ATTACKER\n" 
    outputStream.write(outputString)
    i+=1

