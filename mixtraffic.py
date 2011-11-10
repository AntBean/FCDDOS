#Module for mixing the attacker traffic & User traffic
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

# parse commandline arguments
def parseCmdArgs():
    desc = "Mix attacker & user parameters outputed from parseApacheLog & generate arff file"
    parser = argparse.ArgumentParser(description=desc,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                add_help=False)
    parser.add_argument("-h", "--help", action="help",
            help="Show this help message and exit")
    parser.add_argument("-u", "--user-file",
            help="File container user parameters")
    parser.add_argument("-a", "--attacker-file",
            help="File container attacker parameters")
    parser.add_argument("-o", "--outfile", default="weka.arff",
            help="File to mixed parameters for user & attacker")
    parser.add_argument("-f", "--arff-format",
            help="arff format file")
    args = parser.parse_args()
    return args

#parse commandlist arguments    
args = parseCmdArgs()
outputStream = None
try:
    outputStream = open(args.outfile,"w")
except:
    # happend when the outfile is specified incorrectly 
    # or not specified at all
    outputStream = sys.stdout

try:
    userFile = open(args.user_file,"r")
except IOError:
    print args.user_file,"file open error"
try:
    attackerFile = open(args.attacker_file,"r")
except IOError:
    print args.attacker_file,"file open error"

try:
    arffFormat = open(args.arff_format,"r")
except IOError:
    print args.arff_format,"file open error"

arffLines = arffFormat.readlines()
userLines = userFile.readlines()
attackerLines = attackerFile.readlines()
mixedLines = userLines + attackerLines
#shuffle lines to mix the parameters
random.shuffle(mixedLines)
#append the data lines after arff format lines
finalLines = arffLines+mixedLines
outputStream.writelines(finalLines)
