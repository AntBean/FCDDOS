"""
    Module for mixing the attacker parameter with train & test parameter
    Output will be train & test files in  arff format with attacker parameter 
    mixed in both
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
    parser.add_argument("-T", "--train-file",required = True,
            help="File containing train parameters")
    parser.add_argument("-t", "--test-file",required = True,
            help="File containing test parameters")
    parser.add_argument("-a", "--attacker-file",required = True,
            help="File containing attacker parameters")
    parser.add_argument("-f", "--arff-format",required = True,
            help="arff format file")
    args = parser.parse_args()
    return args

#parse commandlist arguments    
args = parseCmdArgs()
trainInStream = None
testInStream = None
arffInStream = None
attackerInStream = None
#open input files
try:
    trainInStream = open(args.train_file,"r")
except IOError:
    print args.user_file,"file open error"
    exit(0)
try:
    testInStream = open(args.test_file,"r")
except IOError:
    print args.test_file,"file open error"
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
train_out_file = args.train_file+".arff"
test_out_file = args.test_file+".arff"
trainOutStream = None
testOutStream = None
try:
    trainOutStream = open(train_out_file,"w")
except IOError:
    print train_out_file,"file open error"
    exit(0)
try:
    testOutStream = open(test_out_file,"w")
except IOError:
    print test_out_file,"file open error"
    exit(0)



arffLines = arffInStream.readlines()
trainInLines = trainInStream.readlines()
testInLines = testInStream.readlines()
attackerLines = attackerInStream.readlines()

#append the data lines after arff format lines
trainOutLines = arffLines+trainInLines+attackerLines
testOutLines = arffLines+testInLines+attackerLines
trainOutStream.writelines(trainOutLines)
testOutStream.writelines(testOutLines)
