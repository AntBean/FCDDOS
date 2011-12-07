"""
    Module for splitting a parameter file into train & test data
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
    desc = "splitting a parameter file into train & test data"
    parser = argparse.ArgumentParser(description=desc,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                add_help=False)
    parser.add_argument("-h", "--help", action="help",
            help="Show this help message and exit")
    parser.add_argument("-p", "--train-percentage", type= int, default = 66,
            help="size of train data in terms of percentage of input data")
    parser.add_argument("-i", "--apache-parsed-file", required=True,
            help="File container apache log file parsed parameters")
    parser.add_argument("-o", "--outdir", required=True,
            help="output directory for train & test file")
    parser.add_argument("-r", "--random-shuffle", action = 'store_true', \
            default=False, help="enable random shuffling in apache file")
    args = parser.parse_args()
    return args

#parse commandlist arguments    
args = parseCmdArgs()
#create the train & test filename
trainFname = os.path.join(args.outdir,os.path.basename(args.apache_parsed_file)\
                            +"_tr")
testFname = os.path.join(args.outdir,os.path.basename(args.apache_parsed_file)\
                            +"_te")
print "trainfile: ", trainFname
print "testfile: ", testFname
trainOutStream = None
testOutStream = None
try:
    apacheOutStream = open(args.apache_parsed_file,"r")
except IOError:
    print args.apache_parsed_file,"file open error"
    exit(0)

try:
    trainOutStream = open(trainFname,"w")
except IOError:
    print trainFname,"file open error"
    exit(0)

try:
    testOutStream = open(testFname,"w")
except IOError:
    print testFname,"file open error"
    exit(0)

apacheLogLines = apacheOutStream.readlines()
#shuffle lines to mix the parameters
if args.random_shuffle:
    random.shuffle(apacheLogLines)
#get the number of lines for train && test
trainLinesCount = int(float(str(round(float(len(apacheLogLines) *\
                        args.train_percentage)/100))))
testLinesCount = int((len(apacheLogLines)-trainLinesCount))
#get the train & test lines
trainLines = apacheLogLines[0:trainLinesCount]
testLines = apacheLogLines[trainLinesCount:]
#write the train & test lines
trainOutStream.writelines(trainLines)
testOutStream.writelines(testLines)

