"""
    split the input apache log file into multiple apache log files
    the split factor is the number of factore that input set will
    be splitted into
"""
from pyparsing import alphas,nums, dblQuotedString, Combine, Word, Group, \
                        delimitedList, Suppress, removeQuotes

from progressbar import ProgressBar , Percentage, Bar
import string
import datetime
import time
import pyparsing
import argparse
import os, sys
import re
indnt = "  "
indntlevel = 0

# parse commandline arguments
def parseCmdArgs():
    desc = "split the set into multiple sets"
    parser = argparse.ArgumentParser(description=desc,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                add_help=False)
    parser.add_argument("-h", "--help", action="help",
            help="Show this help message and exit")
    parser.add_argument("-i", "--apache-log-file", required=True,
            help="Apache Log File")
    parser.add_argument("-o", "--output-dir", default=None, required=True,
            help="directory to store the output sets")
    parser.add_argument("-f", "--split-factor", type=int, default=2,
            help="Split factor")
    args = parser.parse_args()
    return args



#parse commandlist arguments    
args = parseCmdArgs()
apacheInStream = None
setId = 1;
try: 
    apacheInStream = open(args.apache_log_file)
except:
    print "Apache Log File Open Error", args.apache_log_file
    exit(0)

apacheLogLines = apacheInStream.readlines()
#get the number of lines in each set
LinesPerOutSet = int(len(apacheLogLines)/args.split_factor)
print "LinesPerOutSet: ", LinesPerOutSet
while setId <=args.split_factor:
    #write the lines to the current output set
    outputLines = []
    if setId == args.split_factor:
        outputLines = apacheLogLines[(setId-1)*LinesPerOutSet:]
    else:
        outputLines = apacheLogLines[(setId-1)*LinesPerOutSet:setId*LinesPerOutSet]
    #open a new output set file
    outputFname = os.path.join(args.output_dir,os.path.basename(args.apache_log_file)\
            +str(setId))
    print "output set is: ",outputFname
    outputStream = None
    try:
        outputStream = open(outputFname,"w")
    except:
        print "Error Opening Ouput file: ", outputFname
        exit(0)
    outputStream.writelines(outputLines)
    #close the current output set file
    outputStream.close()
    setId+=1

apacheInStream.close()
