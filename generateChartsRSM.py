from xlrd import open_workbook, empty_cell
import xlrd
import os,sys,argparse
from CreateChart import CreateDotChart
from CreateChart import CreateLineChart
from collections import defaultdict
from array import array
import numpy as np
from numpy import cumsum
import operator
"""
input must be only 3 typesof dirSP,fileSP,Combined#SP
"""
# parse commandline arguments
def parseCmdArgs():
    desc = "generate charts for request semantic model"
    parser = argparse.ArgumentParser(description=desc,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                add_help=False)
    parser.add_argument("-h", "--help", action="help",
            help="Show this help message and exit")
    parser.add_argument("-r", "--report-files", default=None, nargs = '*',
            required = True,
            help="report xls files")
    args = parser.parse_args()
    return args

def processSheetData(sheet,wbOutputDir,col):
    if col == sheet.ncols:
        """
            no more test data is left so return
        """
        return
    trainSetName = str(sheet.name)
    try:
        testSetName = str(sheet.cell(0,col+1).value)
    except:
        print col+1,sheet.ncols
        exit(0)
    chartName = str(os.path.join(wbOutputDir,trainSetName+"_"+testSetName))
    chartTitle = "SeqLen Vs SeqProb "+" "+trainSetName+"_"+testSetName
    xLable = "SeqLen"
    yLable = "SeqProb"
    """
    userData = [name,listSeqLen,listSeqProb]
    """
    userData = [trainSetName+"User",[],[]]
    attackerData = [trainSetName+"Attacker",[],[]]
    chartData = []
    userSeqProbFreq = defaultdict(int)
    attackerSeqProbFreq = defaultdict(int)
    for row in range(2,sheet.nrows):
        seqLen = sheet.cell(row,col+2).value 
        seqProb = sheet.cell(row,col+3).value
        if seqLen == empty_cell.value or seqProb== empty_cell.value:
            break

        userData[1].append(int(seqLen))
        userData[2].append(float(seqProb))
        userSeqProbFreq[float(seqProb)] +=1
    for row in range(2,sheet.nrows):
        seqLen = sheet.cell(row,col+5).value 
        seqProb = sheet.cell(row,col+6).value
        if seqLen == empty_cell.value or seqProb== empty_cell.value:
            break

        attackerData[1].append(int(seqLen))
        attackerData[2].append(float(seqProb))
        attackerSeqProbFreq[float(seqProb)] +=1
    
    #write sequence prov vs lendth data to the dot chart
    chartData=[userData,attackerData]
    CreateDotChart(chartName,chartData,xLable,yLable,chartTitle)
    """ 
    #prepare the cdf data and write it to the cdf chart
    chartCDFName = chartName+"CDF"
    chartCDFTitle = "SeqProb CDF"+" "+trainSetName+"_"+testSetName
    xCDFLable = "SeqProb"
    yCDFLable = "SeqProbFreq"
    userCDFData = [trainSetName+"User",[],[]]
    attackerCDFData = [trainSetName+"Attacker",[],[]]
    chartCDFData = []
    xAxisData = []
    yAxisData = []
    for seqProb in userSeqProbFreq.keys():
        seqFreq = userSeqProbFreq[seqProb]
        xAxisData.append(float(seqProb))
        yAxisData.append(int(seqFreq))
    userCDFData[1] = [x for x in xAxisData]
    sumOfyAxisData = sum(yAxisData)
    userCDFData[2] = [float(y)/sumOfyAxisData for y in yAxisData]
    
    xAxisData = []
    yAxisData = []
    for seqProb in attackerSeqProbFreq.keys():
        seqFreq = attackerSeqProbFreq[seqProb]
        xAxisData.append(float(seqProb))
        yAxisData.append(int(seqFreq))
    attackerCDFData[1] = [x for x in xAxisData]
    sumOfyAxisData = sum(yAxisData)
    attackerCDFData[2] = [float(y)/sumOfyAxisData for y in yAxisData]
    
    chartCDFData = [userCDFData,attackerCDFData]
    CreateLineChart(chartCDFName,chartCDFData,xCDFLable,yCDFLable,chartCDFTitle)
    """    
    #prepare the cdf data and write it to the cdf chart
    chartCDFName = chartName+"CDF"
    chartCDFTitle = "SeqProb CDF"+" "+trainSetName+"_"+testSetName
    xCDFLable = "SeqProb"
    yCDFLable = "SeqProbFreq"
    userCDFData = [trainSetName+"User",[],[]]
    attackerCDFData = [trainSetName+"Attacker",[],[]]
    chartCDFData = []
    
    userxAxisData = []
    useryAxisData = []
    sortedUserRankData = sorted(userSeqProbFreq.iteritems(),\
            key=operator.itemgetter(1), reverse=True)
    userxAxisData = [key for key,value in sortedUserRankData]
    userProbRank = [value for key,value in sortedUserRankData]
    """
    #calculate cdf
    userProbRankCDF = []
    for i in range(len(userProbRank)):
        csum = 0
        for j in range(i,len(userProbRank)):
            csum +=userProbRank[j]
        userProbRankCDF.append(csum)
    userProbRank = userProbRankCDF
    """
    useryAxisData = [float(d)/sum(userProbRank) for d in userProbRank]
    useryAxisData = cumsum(useryAxisData)
    print useryAxisData
    userCDFData[1] = userxAxisData
    userCDFData[2]  = useryAxisData
    
    attackerxAxisData = []
    attackeryAxisData = []
    sortedAttackerRankData = sorted(attackerSeqProbFreq.iteritems(),\
            key=operator.itemgetter(1), reverse=True)
    attackerxAxisData = [key for key,value in sortedAttackerRankData]
    attackerProbRank = [value for key,value in sortedAttackerRankData]
    """
    #calculate cdf
    attackerProbRankCDF = []
    for i in range(len(attackerProbRank)):
        csum = 0
        for j in range(i,len(attackerProbRank)):
            csum +=attackerProbRank[j]
        attackerProbRankCDF.append(csum)
    attackerProbRank = attackerProbRankCDF
    """
    attackeryAxisData = [float(d)/sum(attackerProbRank) for d in attackerProbRank]
    attackeryAxisData = cumsum(attackeryAxisData)
    print attackeryAxisData
    attackerCDFData[1] = attackerxAxisData
    attackerCDFData[2]  = attackeryAxisData
    
    
    chartCDFData = [userCDFData,attackerCDFData]
    CreateLineChart(chartCDFName,chartCDFData,xCDFLable,yCDFLable,chartCDFTitle)
    #process next test results in this sheet
    processSheetData(sheet,wbOutputDir,col+7)
     


#parse commandlist arguments    
args = parseCmdArgs()
#read workbooks
for fileName in args.report_files:
    reportType = str(os.path.basename(fileName).split(".")[0])
    wbOutputDir = str(os.path.dirname(fileName))+"/"+reportType
    print "wbOutputDir",wbOutputDir
    #create the output  directory to hold the charts
    #if already exits, then use it don't recreate it
    try:
        os.mkdir(wbOutputDir,0777)
    except OSError:
        None
    wb = open_workbook(fileName)
    for sheet in wb.sheets():
        print 'Sheet:',sheet.name
        processSheetData(sheet,wbOutputDir,0)

