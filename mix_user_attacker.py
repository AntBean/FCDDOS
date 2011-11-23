"""
    Module for mixing the attacker parameter with user parameter
    Output will be in arff format
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

# parse commandline arguments
def parseCmdArgs():
    desc = "Mix attacker & user parameters outputed from parseApacheLog & generate arff file"
    parser = argparse.ArgumentParser(description=desc,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                add_help=False)
    parser.add_argument("-h", "--help", action="help",
            help="Show this help message and exit")
    parser.add_argument("-u", "--user-file",required = True,
            help="File containing user parameters")
    parser.add_argument("-a", "--attacker-file",required = True,
            help="File containing attacker parameters")
    parser.add_argument("-f", "--arff-format",required = True,
            help="arff format file")
    args = parser.parse_args()
    return args

#parse commandlist arguments    
args = parseCmdArgs()
userInStream = None
arffInStream = None
attackerInStream = None
#open input files
try:
    userInStream = open(args.user_file,"r")
except IOError:
    print args.user_file,"file open error"
    exit(0)
try:
    attackerInStream = open(args.attacker_file,"r")
except IOError:
    print args.attacker_file,"file open error"
    exit(0)
try:
    arffInStream = open(args.arff_format,"r")
except IOError:
    print args.arff_format,"file open error"
    exit(0)
#open output files
out_file = os.path.join(os.path.dirname(args.user_file),\
            os.path.basename(args.user_file)+\
           "_"+os.path.basename(args.attacker_file)+".arff")

OutStream = None
try:
    OutStream = open(out_file,"w")
except IOError:
    print out_file,"file open error"
    exit(0)



arffLines = arffInStream.readlines()
userLines = userInStream.readlines()
attackerLines = attackerInStream.readlines()

#append the data lines after arff format lines
OutLines = arffLines+userLines+attackerLines
OutStream.writelines(OutLines)
