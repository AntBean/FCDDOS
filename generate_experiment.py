#Module for generating a training set & testing in arff format
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
    desc = "module for generating training set & set in arff format"
    parser = argparse.ArgumentParser(description=desc,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                add_help=False)
    parser.add_argument("-h", "--help", action="help",
            help="Show this help message and exit")
    parser.add_argument("-t", "--training-set",required = True,
            nargs='+',
            help="File containing data for training")
    parser.add_argument("-v", "--testing-set",required = True,
            nargs='+',
            help="File containing data for testing")
    parser.add_argument("-to", "--training-ofile",required = True,
            help="File containing the training set in arff format")
    parser.add_argument("-vo", "--testing-ofile",required = True,
            help="File containing the testing set in arff format")
    parser.add_argument("-f", "--arff-format",required = True,
            help="arff format file")
    args = parser.parse_args()
    return args

#parse commandlist arguments    
args = parseCmdArgs()
#list of training file streams
training_fss = []
#list of testing file streams
testing_fss = []
training_ofs = None
testing_ofs = None
arff_fs = None
#open all the files in training set
for tr_file in args.training_set:
    try:
        training_fs = open(tr_file,"r")
        training_fss.append(training_fs)
    except IOError:
        print args.tr_file,"file open error"

#open all the files in testing set 
for ts_file in args.testing_set:
    try:
        testing_fs = open(ts_file,"r")
        testing_fss.append(testing_fs)
    except IOError:
        print args.ts_file,"file open error"

#open the output file for training data
try:
    training_ofs = open(args.training_ofile,"w")
except IOError:
    print args.training_ofile,"file open error"
#open the output file for testing data
try:
    testing_ofs = open(args.testing_ofile,"w")
except IOError:
    print args.testing_ofile,"file open error"
#open the arff format file
try:
    arff_fs = open(args.arff_format,"r")
except IOError:
    print args.arff_fs,"file open error"

#read arff format
arffLines = arff_fs.readlines()
trainingLines = None
testingLines = None
outputLines = None


#create arff formate testing set
for training_fs in training_fss:
    if trainingLines:
        trainingLines+=training_fs.readlines()
    else:
        trainingLines=training_fs.readlines()
try:
    #shuffle lines to mix them
    random.shuffle(trainingLines)
except:
    print "suffle training lines error"
    sys.exit(0)
#append the data lines after arff format lines
outputLines = arffLines+trainingLines
training_ofs.writelines(outputLines)

#now create arff format for testing set
outputLines = None
for testing_fs in testing_fss:
    if testingLines:
        testingLines+=testing_fs.readlines()
    else:
        testingLines=testing_fs.readlines()
try:
    #shuffle lines to mix them
    random.shuffle(testingLines)
except:
    print "suffle testing lines error"
    sys.exit(0)
#append the data lines after arff format lines
outputLines = arffLines+testingLines
testing_ofs.writelines(outputLines)
