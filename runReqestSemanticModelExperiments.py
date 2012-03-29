import os,sys,argparse,pickle
import math, xlwt
from RequestSemanticModel import *
from operator import itemgetter
import copy

"""
set WRITE_ATTACKER_LOGS To True if want to write attacker sequences 
to logs
Warning: setting it to true may results in large attacker logs files
being written to the system
"""
WRITE_ATTACKER_LOGS = False


# parse commandline arguments
def parseCmdArgs():
    desc = "runExperiment for request dynamics model"
    parser = argparse.ArgumentParser(description=desc,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                add_help=False)
    parser.add_argument("-h", "--help", action="help",
            help="Show this help message and exit")
    parser.add_argument("-u", "--unparsed-log-files", default=None, nargs = '*',
            help="Unparsed Apache Log File")
    parser.add_argument("-p", "--parsed-log-files", default=None, nargs = '*',
            help="Unparsed Apache Log File")
    parser.add_argument("-o", "--outdir", default=None, required = True,
            help="Output Directory")
    parser.add_argument("-r", "--attacker-user-ratio", default=1,
            help="attacker to user ratio")
    args = parser.parse_args()
    return args


#parse commandlist arguments    
args = parseCmdArgs()

outputDir = os.path.join(args.outdir,"requestSemanticModel")
parsedDir = os.path.join(args.outdir,"parsed")
#create the parsed directory to hold parsed output parseApache.py
#if already exits, then use it don't recreate it
try:
    os.mkdir(parsedDir,0777)
except OSError:
    None
#create the output  directory to hold request dynamic results
#if already exits, then use it don't recreate it
try:
    os.mkdir(outputDir,0777)
except OSError:
    None

wbDirSP = xlwt.Workbook()
wbFileSP = xlwt.Workbook()
wbCombined1SP = xlwt.Workbook()
#workbook for capturing testing results
wbTestRes = xlwt.Workbook()
wsfp = wbTestRes.add_sheet('FalsePositives')
wsfn = wbTestRes.add_sheet('FalseNegatives')
wsbotcount = wbTestRes.add_sheet('NumberOfBots')
wsMinMBDetails = wbTestRes.add_sheet('minMBDetails')
#add header data to the sheet test results sheets
wsMinMBDetails.write(0,0,"trnSet")
wsMinMBDetails.write(0,1,"method")
wsMinMBDetails.write(0,2,"threshold")
wsMinMBDetails.write(0,3,"tstSet")
wsMinMBDetails.write(0,4,"minMB")
wsMinMBDetails.write(0,5,"minMBId")
wsMinMBDetails.write(0,6,"minMBLen")
wsfp.write(0,0,"trnSet")
wsfp.write(0,1,"method")
wsfp.write(0,2,"threshold")
wsfn.write(0,0,"trnSet")
wsfn.write(0,1,"method")
wsfn.write(0,2,"threshold")
wsbotcount.write(0,0,"trnSet")
wsbotcount.write(0,1,"method")
wsbotcount.write(0,2,"threshold")
testResRow = 0
mainTestResRow = 1
wsMinMBDetRow = 0


models = []
testingSets = []

if (args.unparsed_log_files is None) and (args.parsed_log_files is None):
    print "Atleast one of them is needed: unparsed log file or parsed log file"
if args.unparsed_log_files:
    args.parsed_log_files = []
    for unparsed_log_file in args.unparsed_log_files:
        parsed_log_file = os.path.join(parsedDir,os.path.basename(unparsed_log_file)+
                                        "_u")
        args.parsed_log_files.append(parsed_log_file)
        parseApacheCommand = "python parseApacheLog.py -i "+unparsed_log_file+\
                            " -o "+parsedDir
        print "parsed out file: ",parsed_log_file
        print "Parse apache command: ", parseApacheCommand
        os.system(parseApacheCommand)

olderDataSets = []
for parsed_log_file in args.parsed_log_files:
    outBaseFname = os.path.join(outputDir,os.path.basename(parsed_log_file))
    outBaseFname = str(outBaseFname.partition("_u")[0])

    statsFname = parsed_log_file+"_pickle"

    pickleStream = None
    try:
        pickleStream = open(statsFname,"rb")
    except:
        print "Error Opening pickle file: ",statsFname
        exit(0)
    outStats = pickle.load(pickleStream)
    #print "outStats: ", outStats
    
    dirTrainSequences = outStats[8]
    dirRequestGraph = outStats[9]
    fileTrainSequences = outStats[10]
    fileRequestGraph = outStats[11]
    parentDirToFileGraph = outStats[14]
    combined1TrainSequences = copy.deepcopy(fileTrainSequences)
    
    trnSetId = str(os.path.basename(outBaseFname))
   
    #calculate edge transitional probabilites: generate model data
    dirRequestGraph.calculateEdgeTransitionalProb()
    fileRequestGraph.calculateEdgeTransitionalProb()
    parentDirToFileGraph.calculateEdgeTransitionalProb()

    #get 4 thresholds for experimental purpose
    dirThresholds=getThresholds(dirRequestGraph,dirTrainSequences)
    fileThresholds=getThresholds(fileRequestGraph,fileTrainSequences)
    combined1Thresholds=getThresholdsCombined1(dirRequestGraph,fileRequestGraph,
            parentDirToFileGraph,combined1TrainSequences)
    #print "dirThresholds",dirThresholds
    #print "fileThresholds",fileThresholds
    #print "combined1Thresholds",combined1Thresholds
    
    #display the request graph
    """
    print "##############dir Request Graph Starts#############" 
    fileRequestGraph.show()
    dirRequestGraph.show()
    print "##############dir Request Graph Ends#############" 
    """

    #write models to log file
    dirRequestGraphLogFname = outBaseFname+".dirmodel.log"
    fileRequestGraphLogFname = outBaseFname+".filemodel.log"
    dirFileRequestGraphLogFname = outBaseFname+".dirFilemodel.log"
    dirFileRequestGraphSTDLogFname = outBaseFname+".dirFilemodelSTD.log"
    
    dirRequestGraph.writeToFile(dirRequestGraphLogFname)
    fileRequestGraph.writeToFile(fileRequestGraphLogFname)
    parentDirToFileGraph.writeToFile(dirFileRequestGraphLogFname)
    parentDirToFileGraph.writeSTDToFile(dirFileRequestGraphSTDLogFname)

    #add sheets to capture test results for this model
    wsDirSP = wbDirSP.add_sheet(trnSetId)
    wsFileSP = wbFileSP.add_sheet(trnSetId)
    wsCombined1SP = wbCombined1SP.add_sheet(trnSetId)
    wsDirSP.write(0,0,"DataSetId")
    wsFileSP.write(0,0,"DataSetId")
    wsCombined1SP.write(0,0,"DataSetId")
    headerRow = 0
    headerCol = 1
    
    mainTestResRow += testResRow
    testResCol = 3
    wsMinMBDetRow += 1
   
    for parsedLogFname in args.parsed_log_files:
        testResRow = mainTestResRow
        """
        we don't test when the test data is older than train data
        """
        if parsedLogFname in olderDataSets:
            continue
        testSetFname = parsedLogFname+"_pickle"
        #open the test set pickle file
        testSetPickleStream = None
        try:
            testSetPickleStream = open(testSetFname,"rb")
        except:
            print "Error Opening pickle file: ",testSetFname
            exit(0)
        
        testSetStats = pickle.load(testSetPickleStream)
        
        TotalNumberAttacker = testSetStats[2]
        dirTestSequences = testSetStats[8]
        dirTestRequestGraph = testSetStats[9]
        fileTestSequences = testSetStats[10]
        fileTestRequestGraph = testSetStats[11]
        parentDirToFileTestGraph = testSetStats[14]
        
        #update TotalNumberOfAttacker
        TotalNumberAttacker = (TotalNumberAttacker * int(args.attacker_user_ratio))
        
        #create attacker sequences
        dirTestAttackerSequences = dirTestRequestGraph.getAttackerSequences(\
                TotalNumberAttacker)
        #showSequences(dirAttackerSequences)
        fileTestAttackerSequences = fileTestRequestGraph.getAttackerSequences(\
                TotalNumberAttacker)
        #showSequences(fileAttackerSequences)
        """
        create sequences for combined1 formula
        these are just copy of fileTestSequences
        """
        combined1TestSequences = copy.deepcopy(fileTestSequences)
        combined1TestAttackerSequences = copy.deepcopy(fileTestAttackerSequences)
        
         

        testSetId = str(str(os.path.basename(testSetFname)).split("_")[0])+"te"
        #intilial data for report file
        wsDirSP.write(headerRow,headerCol,testSetId)
        wsDirSP.write(headerRow+1,headerCol,"UserSeqID")
        wsDirSP.write(headerRow+1,headerCol+1,"UserSeqLen")
        wsDirSP.write(headerRow+1,headerCol+2,"UserSeqProb")
        wsDirSP.write(headerRow+1,headerCol+3,"AttackerSeqID")
        wsDirSP.write(headerRow+1,headerCol+4,"AttackerSeqLen")
        wsDirSP.write(headerRow+1,headerCol+5,"AttackerSeqProb")
        
        wsFileSP.write(headerRow,headerCol,testSetId)
        wsFileSP.write(headerRow+1,headerCol,"UserSeqID")
        wsFileSP.write(headerRow+1,headerCol+1,"UserSeqLen")
        wsFileSP.write(headerRow+1,headerCol+2,"UserSeqProb")
        wsFileSP.write(headerRow+1,headerCol+3,"AttackerSeqID")
        wsFileSP.write(headerRow+1,headerCol+4,"AttackerSeqLen")
        wsFileSP.write(headerRow+1,headerCol+5,"AttackerSeqProb")
        
        wsCombined1SP.write(headerRow,headerCol,testSetId)
        wsCombined1SP.write(headerRow+1,headerCol,"UserSeqID")
        wsCombined1SP.write(headerRow+1,headerCol+1,"UserSeqLen")
        wsCombined1SP.write(headerRow+1,headerCol+2,"UserSeqProb")
        wsCombined1SP.write(headerRow+1,headerCol+3,"AttackerSeqID")
        wsCombined1SP.write(headerRow+1,headerCol+4,"AttackerSeqLen")
        wsCombined1SP.write(headerRow+1,headerCol+5,"AttackerSeqProb")

        
        #get the test results by calculating sequence probabilities

        #calculate sequences probabilites and using request
        # graphs from model
        print "\n"
        print "#############Calculating Seq Prog  Started###############"
        # intilize the progress bar
        CalSPProgBarEndStatus = len(dirTestSequences)+\
                                    len(dirTestAttackerSequences)+\
                                    len(fileTestSequences)+\
                                    len(fileTestAttackerSequences)+\
                                    len(combined1TestSequences)+\
                                    len(combined1TestAttackerSequences)
        CalSPProgBarStartStatus = 0
        calSPProgBar = ProgressBar(widgets = [Bar(),Percentage()],\
            maxval=CalSPProgBarEndStatus).start()
        for dirTestSequence in dirTestSequences:
            dirTestSequence.calculateSequenceProb(dirRequestGraph)
            CalSPProgBarStartStatus += 1
            #update the progress bar
            calSPProgBar.update(CalSPProgBarStartStatus)
        for dirTestAttackerSequence in dirTestAttackerSequences:
            dirTestAttackerSequence.calculateSequenceProb(dirRequestGraph)
            CalSPProgBarStartStatus += 1
            #update the progress bar
            calSPProgBar.update(CalSPProgBarStartStatus)
        for fileTestSequence in fileTestSequences:
            fileTestSequence.calculateSequenceProb(fileRequestGraph)
            CalSPProgBarStartStatus += 1
            #update the progress bar
            calSPProgBar.update(CalSPProgBarStartStatus)
        for fileTestAttackerSequence in fileTestAttackerSequences:
            fileTestAttackerSequence.calculateSequenceProb(fileRequestGraph)
            CalSPProgBarStartStatus += 1
        for combined1TestSequence in combined1TestSequences:
            combined1TestSequence.calculateSequenceProbCombined1(dirRequestGraph,\
                    fileRequestGraph,parentDirToFileGraph)
            CalSPProgBarStartStatus += 1
            #update the progress bar
            calSPProgBar.update(CalSPProgBarStartStatus)
        for combined1TestAttackerSequence in combined1TestAttackerSequences:
            combined1TestAttackerSequence.calculateSequenceProbCombined1(\
                    dirRequestGraph,fileRequestGraph,parentDirToFileGraph)
            CalSPProgBarStartStatus += 1
            #update the progress bar
            calSPProgBar.update(CalSPProgBarStartStatus)
        print "#############Calculating Seq Prog  Ended###############"
        print "\n"

        print "#################TestingSequences starts##################"
        dirTestResults = testSequences(dirRequestGraph,dirTestSequences,\
                dirTestAttackerSequences,dirThresholds)
        fileTestResults = testSequences(fileRequestGraph,fileTestSequences,\
                fileTestAttackerSequences,fileThresholds)
        combined1TestResults = testSequencesCombined1(dirRequestGraph,\
                fileRequestGraph,parentDirToFileGraph,combined1TestSequences,\
                combined1TestAttackerSequences,combined1Thresholds)
        """
        print "dirTestResults: "
        for tdict in dirTestResults:
            print sorted(tdict.iteritems(),key=itemgetter(0),reverse=True)
        """
        print "#################TestingSequences Ends####################"

        print "#############Writing data to report file Started###############"
        #write test results: seq prob to report files
        #write user dir sequence probability data to the report file
        wsDirSPRow = headerRow+2
        wsDirSPCol = headerCol
        for dirTestSequence in dirTestSequences:
            wsDirSP.write(wsDirSPRow,wsDirSPCol,\
                    dirTestSequence.getId())
            wsDirSP.write(wsDirSPRow,wsDirSPCol+1,\
                    dirTestSequence.getSequenceLength())
            wsDirSP.write(wsDirSPRow,wsDirSPCol+2,\
                    dirTestSequence.getSequenceProb())
            wsDirSPRow += 1

        #write attacker dir sequence probability data to the report file
        wsDirSPRow = headerRow+2
        wsDirSPCol = headerCol
        for dirTestAttackerSequence in dirTestAttackerSequences:
            wsDirSP.write(wsDirSPRow,wsDirSPCol+3,\
                    dirTestAttackerSequence.getId())
            wsDirSP.write(wsDirSPRow,wsDirSPCol+4,\
                    dirTestAttackerSequence.getSequenceLength())
            wsDirSP.write(wsDirSPRow,wsDirSPCol+5,\
                    dirTestAttackerSequence.getSequenceProb())
            wsDirSPRow += 1
        
        #write user file sequence probability data to the report file
        wsFileSPRow = headerRow+2
        wsFileSPCol = headerCol
        for fileTestSequence in fileTestSequences:
            wsFileSP.write(wsFileSPRow,wsFileSPCol,\
                    fileTestSequence.getId())
            wsFileSP.write(wsFileSPRow,wsFileSPCol+1,\
                    fileTestSequence.getSequenceLength())
            wsFileSP.write(wsFileSPRow,wsFileSPCol+2,\
                    fileTestSequence.getSequenceProb())
            wsFileSPRow += 1

        #write attacker file sequence probability data to the report file
        wsFileSPRow = headerRow+2
        wsFileSPCol = headerCol
        for fileTestAttackerSequence in fileTestAttackerSequences:
            wsFileSP.write(wsFileSPRow,wsFileSPCol+3,\
                    fileTestAttackerSequence.getId())
            wsFileSP.write(wsFileSPRow,wsFileSPCol+4,\
                    fileTestAttackerSequence.getSequenceLength())
            wsFileSP.write(wsFileSPRow,wsFileSPCol+5,\
                    fileTestAttackerSequence.getSequenceProb())
            wsFileSPRow += 1
        
        #write user combined1 sequence probability data to the report file
        wsCombined1SPRow = headerRow+2
        wsCombined1SPCol = headerCol
        for combined1TestSequence in combined1TestSequences:
            wsCombined1SP.write(wsCombined1SPRow,wsCombined1SPCol,\
                    combined1TestSequence.getId())
            wsCombined1SP.write(wsCombined1SPRow,wsCombined1SPCol+1,\
                    combined1TestSequence.getSequenceLength())
            wsCombined1SP.write(wsCombined1SPRow,wsCombined1SPCol+2,\
                    combined1TestSequence.getSequenceProb())
            wsCombined1SPRow += 1

        #write attacker combined1 sequence probability data to the report file
        wsCombined1SPRow = headerRow+2
        wsCombined1SPCol = headerCol
        for combined1TestAttackerSequence in combined1TestAttackerSequences:
            wsCombined1SP.write(wsCombined1SPRow,wsCombined1SPCol+3,\
                    combined1TestAttackerSequence.getId())
            wsCombined1SP.write(wsCombined1SPRow,wsCombined1SPCol+4,\
                    combined1TestAttackerSequence.getSequenceLength())
            wsCombined1SP.write(wsCombined1SPRow,wsCombined1SPCol+5,\
                    combined1TestAttackerSequence.getSequenceProb())
            wsCombined1SPRow += 1

        #print "###########dir sequence Probabilites starts###########"
        #showSequencesProb(dirTestSequences)
        #print "###########dir sequence Probabilites Ends###########"
        #print "###########file sequence Probabilites starts###########"
        #showSequencesProb(fileTestSequences)
        #print "###########file sequence Probabilites Ends###########"
        #update header col
        headerCol +=7
        print "#############Writing data to report file Ended###############"
        print "\n"
        
        #write test results to the xls sheet
        if testResCol ==3:
            wsfp.write(testResRow, 0, trnSetId)
            wsfn.write(testResRow, 0, trnSetId)
            wsbotcount.write(testResRow, 0, trnSetId)
        if testResRow ==1:
            wsfp.write(0, testResCol, testSetId)
            wsfn.write(0, testResCol, testSetId)
            wsbotcount.write(0, testResCol, testSetId)
        testResultsIndex = 0
        for testResults in [dirTestResults,fileTestResults,\
            combined1TestResults]:
            methodName = None
            thresholds = None
            if testResultsIndex ==0:
                methodName = "dir"
                thresholds = dirThresholds
            elif testResultsIndex ==1:
                methodName = "file"
                thresholds = fileThresholds
            elif testResultsIndex ==2:
                methodName = "combined1"
                thresholds = combined1Thresholds
            else:
                print "invalid method name"
                exit(0)
            for threshold in thresholds:
                if testResCol ==3:
                    wsfp.write(testResRow, 1, methodName)
                    wsfp.write(testResRow, 2, str(threshold))
                    wsfn.write(testResRow, 1, methodName)
                    wsfn.write(testResRow, 2, str(threshold))
                    wsbotcount.write(testResRow, 1, methodName)
                    wsbotcount.write(testResRow, 2, str(threshold))
    
                wsfp.write(testResRow, testResCol, str(testResults[0][threshold]))
                wsfn.write(testResRow, testResCol, str(testResults[1][threshold]))
                wsbotcount.write(testResRow, testResCol,\
                        str(testResults[2][threshold][0]))

                wsMinMBDetails.write(wsMinMBDetRow,0,trnSetId)
                wsMinMBDetails.write(wsMinMBDetRow,1,methodName)
                wsMinMBDetails.write(wsMinMBDetRow,2,threshold)
                wsMinMBDetails.write(wsMinMBDetRow,3,testSetId)
                wsMinMBDetails.write(wsMinMBDetRow,4,\
                        str(testResults[2][threshold][0]))
                wsMinMBDetails.write(wsMinMBDetRow,5,\
                        str(testResults[2][threshold][1]))
                wsMinMBDetails.write(wsMinMBDetRow,6,\
                        str(testResults[2][threshold][2]))
                wsMinMBDetRow +=1

                testResRow +=1
            testResultsIndex +=1
        testResCol+=1

        #write test resutl to log files
        print "#############Writing data to log file Started###############"
        startTestLogFname = outBaseFname+"_"+testSetId
        dirUserSPLogFname = startTestLogFname+".dirUserSP.log"
        dirAttackerSPLogFname = startTestLogFname+".dirAttackerSP.log"
        fileUserSPLogFname = startTestLogFname+".fileUserSP.log"
        fileAttackerSPLogFname = startTestLogFname+".fileAttackerSP.log"
        combined1UserSPLogFname = startTestLogFname+".combined1UserSP.log"
        combined1AttackerSPLogFname = startTestLogFname+".combined1AttackerSP.log"
        
        

        writeSequencesProbToFile(dirTestSequences, dirUserSPLogFname)
        writeSequencesProbToFile(fileTestSequences, fileUserSPLogFname)
        writeSequencesProbToFile(combined1TestSequences, combined1UserSPLogFname)
        if WRITE_ATTACKER_LOGS:
            writeSequencesProbToFile(dirTestAttackerSequences,\
                    dirAttackerSPLogFname)
            #writeAttackerSequencesProbToFile(dirTestAttackerSequences, dirAttackerSPLogFname)
            writeSequencesProbToFile(fileTestAttackerSequences,\
                    fileAttackerSPLogFname)
            #writeAttackerSequencesProbToFile(fileTestAttackerSequences, fileAttackerSPLogFname)
            writeSequencesProbToFile(combined1TestAttackerSequences,\
                    combined1AttackerSPLogFname)
        #writeAttackerSequencesProbToFile(combined1TestAttackerSequences,\
        #        combined1AttackerSPLogFname)
        
        #write classification result to text file
        logDataList = [[dirThresholds,dirTestSequences,\
                      dirTestAttackerSequences],\
                      [fileThresholds,fileTestSequences,\
                      fileTestAttackerSequences],\
                      [combined1Thresholds,combined1TestSequences,\
                      combined1TestAttackerSequences]\
                      ]
        #logDataListIndex = 0
        for logDataListIndex in range(len(logDataList)):
            methodName = None
            logData = logDataList[logDataListIndex]
            if logDataListIndex == 0:
                methodName = "dir"
            elif logDataListIndex == 1:
                methodName = "file"
            elif logDataListIndex == 2:
                methodName = "combined1"
            for logDataThreshold in logData[0]:
                testResUserLogFname = startTestLogFname+"."+methodName+\
                                      ".User"+str(logDataThreshold)+".classification"
                testResAttackerLogFname = startTestLogFname+"."+methodName+\
                                      ".Attacker"+str(logDataThreshold)+".classification"
                writeSeqClassificationToFile(logData[1],\
                        testResUserLogFname,logDataThreshold)
                writeSeqClassificationToFile(logData[2],\
                        testResAttackerLogFname,logDataThreshold)
            logDataListIndex += 1
        print "#############Writing data to log file Ended###############"
        
    #add this file to olderDataSets
    olderDataSets.append(parsed_log_file)
    
    """
    for now we will train only with first data set and test with itself and 
    rest
    """
    break;

try:    
    #wb.save('report.xls')
    wbDirSP.save(os.path.join(outputDir,os.path.basename(\
                    'dirSeqProb.xls')))
    wbFileSP.save(os.path.join(outputDir,os.path.basename(\
                    'fileSeqProb.xls')))
    wbCombined1SP.save(os.path.join(outputDir,os.path.basename(\
                    'combined1SeqProb.xls')))
    wbTestRes.save(os.path.join(outputDir,os.path.basename(\
                    'testResult.xls')))
except Exception as e:
    print e.args
    print e
