import os,sys,argparse,pickle
import math, xlwt
from RequestSemanticModel import *
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
    
    dirRequestGraph = outStats[16]
    fileRequestGraph = outStats[18]
    
    trnSetId = str(os.path.basename(outBaseFname))
   
    #calculate edge transitional probabilites: generate model data
    dirRequestGraph.calculateEdgeTransitionalProb()
    fileRequestGraph.calculateEdgeTransitionalProb()
    #display the request graph
    #print "##############dir Request Graph Starts#############" 
    #fileRequestGraph.show()
    #print "##############dir Request Graph Ends#############" 

    #write models to log file
    dirRequestGraphLogFname = outBaseFname+".model.log"
    dirRequestGraph.writeToFile(dirRequestGraphLogFname)

    #add sheets to capture test results for this model
    wsDirSP = wbDirSP.add_sheet(trnSetId)
    wsFileSP = wbFileSP.add_sheet(trnSetId)
    wsCombined1SP = wbCombined1SP.add_sheet(trnSetId)
    wsDirSP.write(0,0,"DataSetId")
    wsFileSP.write(0,0,"DataSetId")
    wsCombined1SP.write(0,0,"DataSetId")
    headerRow = 0
    headerCol = 1
    for parsedLogFname in args.parsed_log_files:
        testSetFname = parsedLogFname+"_pickle"
        #open the test set pickle file
        testSetPickleStream = None
        try:
            testSetPickleStream = open(testSetFname,"rb")
        except:
            print "Error Opening pickle file: ",testSetFname
            exit(0)
        
        testSetStats = pickle.load(testSetPickleStream)
        
        TotalNumberAttacker = testSetStats[9]
        dirTestSequences = testSetStats[15]
        dirTestRequestGraph = testSetStats[16]
        fileTestSequences = testSetStats[17]
        fileTestRequestGraph = testSetStats[18]
        
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
        combined1TestSequences = list(fileTestSequences)
        combined1TestAttackerSequences = list(fileTestAttackerSequences)

         

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
                    fileRequestGraph)
            CalSPProgBarStartStatus += 1
            #update the progress bar
            calSPProgBar.update(CalSPProgBarStartStatus)
        for combined1TestAttackerSequence in combined1TestAttackerSequences:
            combined1TestAttackerSequence.calculateSequenceProbCombined1(\
                    dirRequestGraph,fileRequestGraph)
            CalSPProgBarStartStatus += 1
            #update the progress bar
            calSPProgBar.update(CalSPProgBarStartStatus)
        print "#############Calculating Seq Prog  Ended###############"
        print "\n"

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
        writeSequencesProbToFile(dirTestAttackerSequences, dirAttackerSPLogFname)
        writeSequencesProbToFile(fileTestSequences, fileUserSPLogFname)
        writeSequencesProbToFile(fileTestAttackerSequences, fileAttackerSPLogFname)
        writeSequencesProbToFile(combined1TestSequences, combined1UserSPLogFname)
        writeSequencesProbToFile(combined1TestAttackerSequences,\
                combined1AttackerSPLogFname)
        print "#############Writing data to log file Ended###############"
        

try:    
    #wb.save('report.xls')
    wbDirSP.save(os.path.join(outputDir,os.path.basename(\
                    'dirSeqProb.xls')))
    wbFileSP.save(os.path.join(outputDir,os.path.basename(\
                    'fileSeqProb.xls')))
    wbCombined1SP.save(os.path.join(outputDir,os.path.basename(\
                    'combined1SeqProb.xls')))
except Exception as e:
    print e.args
    print e
