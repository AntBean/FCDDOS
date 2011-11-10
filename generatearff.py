#Module for converting parsed data into arff file format
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
    desc = "take output from parseApacheLog & generate arff file"
    parser = argparse.ArgumentParser(description=desc,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                add_help=False)
    parser.add_argument("-h", "--help", action="help",
            help="Show this help message and exit")
    parser.add_argument("-i", "--input-file", required=True,
            help="File container parameters")
    parser.add_argument("-o", "--outfile", default=None,
            help="File in arff format")
    parser.add_argument("-f", "--arff-format", required=True,
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
    inputFile = open(args.input_file,"r")
except IOError:
    print args.input_file,"file open error"

try:
    arffFormat = open(args.arff_format,"r")
except IOError:
    print args.arff_format,"file open error"

arffLines = arffFormat.readlines()
inputLines = inputFile.readlines()
#append the data lines after arff format lines
finalLines = arffLines+inputLines
outputStream.writelines(finalLines)
