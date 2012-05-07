import os,sys,argparse
from CreateChart import CreateDotChart
from collections import defaultdict
from array import array
import numpy as np
from numpy import cumsum
import operator
"""
input must be attacker and user seq prob file
"""
# parse commandline arguments
def parseCmdArgs():
    desc = "generate chart for attacker and user seq prob vs len data"
    parser = argparse.ArgumentParser(description=desc,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                add_help=False)
    parser.add_argument("-h", "--help", action="help",
            help="Show this help message and exit")
    parser.add_argument("-u", "--user-file", required = True,
            help="user seq prob file")
    parser.add_argument("-a", "--attacker-file", required = True,
            help="attacker seq prob file")
    parser.add_argument("-o", "--output-dir", required = True,
            help="output directory name")
    args = parser.parse_args()
    return args

"""
parse CVS file and return x axis and y axis data
"""
def parseCVSFile(inFile):
    try:
        f = open(inFile,'rb')
    except IOError:
        print "File ",inFile," does not exists"
        raise
    x = []
    y = []
    for line in f.readlines():
        parsedLine = line.split(',')
        x.append(parsedLine[1])
        y.append(parsedLine[2])

    return x,y

#parse commandlist arguments    
args = parseCmdArgs()

combinedChart = os.path.join(args.output_dir,os.path.basename(args.user_file)+
        os.path.basename(args.attacker_file))
userChart = os.path.join(args.output_dir,os.path.basename(args.user_file))
attackerChart = os.path.join(args.output_dir,os.path.basename(args.attacker_file))
#create the output  directory to hold the charts
#if already exits, then use it don't recreate it
try:
    os.mkdir(args.output_dir,0777)
except OSError:
    None

xLable = "SeqLen"
yLable = "SeqProb"
chartTitle = "SeqLen Vs SeqProb"

userx,usery = parseCVSFile(args.user_file)
attx,atty = parseCVSFile(args.attacker_file)

userData = ["User",userx,usery]
attackerData = ["Attacker",attx,atty] 
chartData = [userData]
CreateDotChart(combinedChart,chartData,xLable,yLable,chartTitle)
