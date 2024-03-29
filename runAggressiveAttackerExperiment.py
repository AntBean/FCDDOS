import os,sys,argparse,pickle,copy,shutil
import math, xlwt
from RequestSemanticModel import writeSequencesProbToFile
from FcddosUtilities import *
"""
convert user or attacker paramerter to string form
"""
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
    parser.add_argument("-m", "--request-mapping", required=True,
            help="request mapping pickle file")
    parser.add_argument("-o", "--outdir", default=None, required = True,
            help="Output Directory")
    parser.add_argument("-r", "--attacker-user-ratio", default=1,
            help="attacker to user ratio")
    parser.add_argument("-t", "--attacker-user-train-ratio", default=1,
            help="attacker to user train ratio")
    args = parser.parse_args()
    return args


#parse commandlist arguments    
args = parseCmdArgs()

#create the output directory 
#if already exits, then use it don't recreate it
try:
    os.mkdir(args.outdir,0777)
except OSError:
    None

wb = xlwt.Workbook()
wsstats = wb.add_sheet('DataSetStats')
wsfp = wb.add_sheet('FalsePositives')
wsfn = wb.add_sheet('FalseNegatives')
wsbotcount = wb.add_sheet('NumberOfBots')
wsfileExtnAccessFrequency = wb.add_sheet('fileExtnAccessFrequency')
wsMinMBDetails = wb.add_sheet('minMBDetails')
wsSequencesProb = wb.add_sheet('sequencesProb')
wsFileSequencesProb = wb.add_sheet('fileSequencesProb')
 

models = []
testingSets = []
if (args.unparsed_log_files is None) and (args.parsed_log_files is None):
    print "Atleast one of them is needed: unparsed log file or parsed log file"
if args.unparsed_log_files:
    args.parsed_log_files = []
    for unparsed_log_file in args.unparsed_log_files:
        parsed_log_file = os.path.join(args.outdir,os.path.basename(unparsed_log_file)+
                                        "_u")
        args.parsed_log_files.append(parsed_log_file)
        """
        default duaration for sesion types
        """
        parseApacheCommand = "python parseApacheLog.py -i "+unparsed_log_file+\
                              " -m "+args.request_mapping+\
                            " -o "+args.outdir
        """
        parseApacheCommand = "python parseApacheLog.py -i "+unparsed_log_file+\
                                " -s "+"20"+\
                                " -b "+"120"+\
                                " -r "+"600"+\
                                " -l "+"1200"+\
                                " -o "+args.outdir
        """
        print "parsed out file: ",parsed_log_file
        print "Parse apache command: ", parseApacheCommand
        os.system(parseApacheCommand)

#intiliazed data for sequencesProb sheet
wsSequencesProb.write(0,0,"sequenceID")
wsSequencesProb.write(0,1,"sequenceProb")
wsSequencesProb.write(0,2,"sequenceLength")
wsFileSequencesProb.write(0,0,"sequenceID")
wsFileSequencesProb.write(0,1,"sequenceProb")
wsFileSequencesProb.write(0,2,"sequenceLength")

#intiliazed data for file access frequency sheet
wsfileExtnAccessFrequency.write(0, 0, "ID")
wsfileExtnAccessFrequency.write(0, 1, "FileExtn")
wsfileExtnAccessFrequency.write(0, 2, "Count")
wsFEAFRow = 1

#intilize data for minMBDetails sheet
wsMinMBDetails.write(0,0,"trnSet");
wsMinMBDetails.write(0,1,"tstSet");
wsMinMBDetails.write(0,2,"minMB");
wsMinMBDetails.write(0,3,"minMBNPra");

#intiliazed data for datastats sheet
wsstats.write(0, 0, "ID")
wsstats.write(0, 1, "#User")
wsstats.write(0, 2, "#Attacker")
wsstats.write(0, 3, "#ValidReq")
wsstats.write(0, 4, "#InvalidFormatReq")
wsstats.write(0, 5, "#InvalidNPraReq")
wsstats.write(0, 6, "#LogCount")
wsstats.write(0, 8, "[N1Min-N1Max]")
wsstats.write(0, 9, "[P1Min-P1Max]")
wsstats.write(0, 10, "[r1Min-r1Max]")
wsstats.write(0, 11, "[a1Min-a1Max]")
wsstats.write(0, 12, "[N2Min-N2Max]")
wsstats.write(0, 13, "[P2Min-P2Max]")
wsstats.write(0, 14, "[N3Min-N3Max]")
wsstats.write(0, 15, "[P3Min-P3Max]")
wsstats.write(0, 16, "[N4Min-N4Max]")
wsstats.write(0, 17, "[P4Min-P4Max]")
statsRowIndx = 1

#most aggressive attacker parameter
aggAttParam = None

#first set the parameter for the most aggressive attacker
for parsed_log_file in args.parsed_log_files:
    statsFname = parsed_log_file+"_pickle"
    #print "stats file name: ",statsFname

    pickleStream = None
    try:
        pickleStream = open(statsFname,"rb")
    except:
        print "Error Opening pickle file: ",statsFname
        exit(0)
    outStats = pickle.load(pickleStream)
    #get attacker param for this data set
    attParam = outStats[0]
    #set most aggressive attacker parameters
    if aggAttParam is None:
        aggAttParam = copy.deepcopy(attParam)
    else:
        for attParamIndex in range(len(attParam)):
            #set minimum value
            if aggAttParam[attParamIndex][0] > attParam[attParamIndex][0]:
                aggAttParam[attParamIndex][0] = attParam[attParamIndex][0]
            #set maximum value
            if aggAttParam[attParamIndex][1] < attParam[attParamIndex][1]:
                aggAttParam[attParamIndex][1] = attParam[attParamIndex][1]
                
                
#convert parameter to str format
floatRoundValue = 2
aggAttParam = convertListToStr(aggAttParam,floatRoundValue)

for parsed_log_file in args.parsed_log_files:
    outBaseFname = os.path.join(args.outdir,os.path.basename(parsed_log_file))
    statsFname = parsed_log_file+"_pickle"
    print "stats file name: ",statsFname

    pickleStream = None
    try:
        pickleStream = open(statsFname,"rb")
    except:
        print "Error Opening pickle file: ",statsFname
        exit(0)
    outStats = pickle.load(pickleStream)
    #print "outStats: ", outStats
    #attacker parameters
    TotalNumberUser = outStats[1]
    TotalNumberAttacker = outStats[2]
    TotalNumberReq = outStats[3]
    invalidFormatCount = outStats[4]
    invalidNPraCount = outStats[5]
    totalLogCount = outStats[6]
    fileExtnAccessFrequencyTable = outStats[7]
    sequences = outStats[8]
    requestGraph = outStats[9]
    fileSequences = outStats[10]
    fileRequestGraph = outStats[11]

    #update TotalNumberOfAttacker
    TotalNumberTrainAttacker = (TotalNumberAttacker * int(
                args.attacker_user_train_ratio))
    TotalNumberTestAttacker = (TotalNumberAttacker * int(
                args.attacker_user_ratio))
    
    ID = str(os.path.basename(parsed_log_file).partition("_u")[0])
    #write stats data to report file
    wsstats.write(statsRowIndx, 0, ID)
    wsstats.write(statsRowIndx, 1, TotalNumberUser)
    wsstats.write(statsRowIndx, 2, TotalNumberAttacker)
    wsstats.write(statsRowIndx, 3, TotalNumberReq)
    wsstats.write(statsRowIndx, 4, invalidFormatCount)
    wsstats.write(statsRowIndx, 5, invalidNPraCount)
    wsstats.write(statsRowIndx, 6, totalLogCount)
    """
    wsstats.write(statsRowIndx, 8, "["+str(minN1)+"-"+str(maxN1)+"]")
    wsstats.write(statsRowIndx, 9, "["+str(minP1)+"-"+str(maxP1)+"]")
    wsstats.write(statsRowIndx, 10, "["+str(minr1)+"-"+str(maxr1)+"]")
    wsstats.write(statsRowIndx, 11, "["+str(mina1)+"-"+str(maxa1)+"]")
    """
    for paramIndex in range(len(aggAttParam)):
        curParam = aggAttParam[paramIndex]
        wsstats.write(statsRowIndx, 8+paramIndex,
                "["+str(curParam[0])+"-"+str(curParam[1])+"]")
        

    statsRowIndx+=1
   
    #write file access frequency table data to report file
    print "#######################file access frequecy########################"
    for key in fileExtnAccessFrequencyTable.keys():
        wsfileExtnAccessFrequency.write(wsFEAFRow, 0, ID)
        wsfileExtnAccessFrequency.write(wsFEAFRow, 1, key)
        wsfileExtnAccessFrequency.write(wsFEAFRow, 2, fileExtnAccessFrequencyTable[key])
        wsFEAFRow += 1
    
    """
    for key in fileExtnAccessFrequencyTable.keys():
        print key,"\t",fileExtnAccessFrequencyTable[key] 
    """
    print "#######################file access frequecy########################"


    #attackerOutFname = str(parsed_log_file.partition("_u")[0])+"_a"
    attackerOutFname = str(outBaseFname.partition("_u")[0])+"_a"
    #run attack_generate command
    """
    attackGenerateCmd ="python attack_generate.py -o "+attackerOutFname+\
                        " -n "+str(TotalNumberAttacker)+\
                        " -N "+str(minN1)+"-"+str(maxN1)+\
                        " -P "+str(minP1)+"-"+str(maxP1)+\
                        " -r "+str(minr1)+"-"+str(maxr1)+\
                        " -a "+str(mina1)+"-"+str(maxa1)
    """
    attackGenerateCmd ="python attack_generate.py -o "+attackerOutFname+\
                        " -n "+str(TotalNumberTrainAttacker)+\
                        " -N "+aggAttParam[0][0]+"-"+aggAttParam[0][1]+\
                        " -P "+aggAttParam[1][0]+"-"+aggAttParam[1][1]+\
                        " -r "+aggAttParam[2][0]+"-"+aggAttParam[2][1]+\
                        " -a "+aggAttParam[3][0]+"-"+aggAttParam[3][1]+\
                        " -N2 "+aggAttParam[4][0]+"-"+aggAttParam[4][1]+\
                        " -P2 "+aggAttParam[5][0]+"-"+aggAttParam[5][1]+\
                        " -N3 "+aggAttParam[6][0]+"-"+aggAttParam[6][1]+\
                        " -P3 "+aggAttParam[7][0]+"-"+aggAttParam[7][1]+\
                        " -N4 "+aggAttParam[8][0]+"-"+aggAttParam[8][1]+\
                        " -P4 "+aggAttParam[9][0]+"-"+aggAttParam[9][1]

    print attackGenerateCmd
    os.system(attackGenerateCmd)

    #split user set into train & test set
    splitIntoTrTeSetCmd1 ="python splitinto_train_test.py -i "+\
                        parsed_log_file+\
                        " -o "+args.outdir+" -r"
    print "splitIntoTrTeSetCmd1: ",splitIntoTrTeSetCmd1
    os.system(splitIntoTrTeSetCmd1)

    #split attacker set into train & test set
    splitIntoTrTeSetCmd2 ="python splitinto_train_test.py -i "+\
                        attackerOutFname+\
                        " -o "+args.outdir+" -r"
    print "splitIntoTrTeSetCmd2: ",splitIntoTrTeSetCmd2
    os.system(splitIntoTrTeSetCmd2)

    #mix user & attacker training set
    #userTrFname = parsed_log_file+"_tr"
    userTrFname = outBaseFname+"_tr"
    attackerTrFname = attackerOutFname+"_tr"
    mixTrCmd = "python mix_user_attacker.py -u "+userTrFname+\
            " -a "+attackerTrFname+\
            " -f arffFormat"
    print "mixTrCmd", mixTrCmd
    os.system(mixTrCmd)
    #mix user & attacker testing set
    #userTeFname = parsed_log_file+"_te"
    userTeFname = outBaseFname+"_te"
    attackerTeFname = attackerOutFname+"_te"
    mixTeCmd = "python mix_user_attacker.py -u "+userTeFname+\
            " -a "+attackerTeFname+\
            " -f arffFormat"
    print "mixTeCmd", mixTeCmd
    os.system(mixTeCmd)

    #generate model using weka
    envVar = "export CLASSPATH=/home/natty/weka/weka.jar:$CLASSPATH"
    trFname = userTrFname+"_"+str(os.path.basename(attackerTrFname))+".arff"   
    modelFname = userTrFname+"_"+str(os.path.basename(attackerTrFname))+".model"
    trResultsFname = userTrFname+"_"+str(os.path.basename(attackerTrFname))+".trainResults"
    generateModelCmd = "java -Xms32m -Xmx2048m weka.classifiers.trees.J48 -t "+trFname+\
                   " -d "+modelFname+\
                   " > "+trResultsFname
    print "trFname: ",trFname
    print "modelFname: ",modelFname
    print "trResultsFname: ",trResultsFname
    print "generateModelCmd: ",generateModelCmd
    os.system(envVar)
    os.system(generateModelCmd)

    """
    needed when 100% user and attacker needed in testset
    """
    #create test sets
    """
    needed for 100 % user test set
    """
    #create the user testing set(includes all user)
    shutil.copy(parsed_log_file, userTeFname)
    #create the aggressive attacker set(includes all attacker)
    """
    needed for 33 % attacker test set
    attackGenerateCmd ="python attack_generate.py -o "+attackerOutFname+\
    """
    attackGenerateCmd ="python attack_generate.py -o "+attackerTeFname+\
                        " -n "+str(TotalNumberTestAttacker)+\
                        " -N "+aggAttParam[0][0]+"-"+aggAttParam[0][1]+\
                        " -P "+aggAttParam[1][0]+"-"+aggAttParam[1][1]+\
                        " -r "+aggAttParam[2][0]+"-"+aggAttParam[2][1]+\
                        " -a "+aggAttParam[3][0]+"-"+aggAttParam[3][1]+\
                        " -N2 "+aggAttParam[4][0]+"-"+aggAttParam[4][1]+\
                        " -P2 "+aggAttParam[5][0]+"-"+aggAttParam[5][1]+\
                        " -N3 "+aggAttParam[6][0]+"-"+aggAttParam[6][1]+\
                        " -P3 "+aggAttParam[7][0]+"-"+aggAttParam[7][1]+\
                        " -N4 "+aggAttParam[8][0]+"-"+aggAttParam[8][1]+\
                        " -P4 "+aggAttParam[9][0]+"-"+aggAttParam[9][1]
    print attackGenerateCmd
    os.system(attackGenerateCmd)
    """
    needed to for 33% attacker test
    #split attacker set into train & test set
    splitIntoTrTeSetCmd2 ="python splitinto_train_test.py -i "+\
                        attackerOutFname+\
                        " -o "+args.outdir+" -r"
    print "splitIntoTrTeSetCmd2: ",splitIntoTrTeSetCmd2
    os.system(splitIntoTrTeSetCmd2)
    """

    #mix user & attacker testing set
    mixTeCmd = "python mix_user_attacker.py -u "+userTeFname+\
            " -a "+attackerTeFname+\
            " -f arffFormat"
    print "mixTeCmd", mixTeCmd
    os.system(mixTeCmd)
    #update models & testingSets
    models.append(modelFname)
    teFname = userTeFname +"_"+ str(os.path.basename(attackerTeFname))+".arff"
    testingSets.append(teFname)

misclassificationFiles = []
testResultFiles = []
for model in models:
    for testSet in testingSets:
        testResultFname = model+"."+str(os.path.basename(testSet))+".testResults"
        testResultFiles.append(testResultFname)
        testCmd = "java -Xms32m -Xmx2048m weka.classifiers.trees.J48"+\
                    " -T "+testSet+" -l "+model+\
                    " -i > "+testResultFname
        print testCmd
        os.system(testCmd)
        misclassificationFname =  model+"."+str(os.path.basename(testSet))+\
                                    ".misclassfication"
        misclassificationFiles.append(misclassificationFname)
        misclassificationCmd = "java -Xms32m -Xmx2048m weka.classifiers.trees.J48"+\
                                " -T "+testSet+\
                                " -l "+model+" -i -p 1-10 | grep '+' > "+\
                                misclassificationFname
        print misclassificationCmd
        os.system(misclassificationCmd)
    break
#generate report
wsfp.write(0, 0, "FP")
wsfn.write(0, 0, "FN")
wsbotcount.write(0,0,"#BotsNeeded")

#Get FP and FN
col = 1 #since col 0 is already written
row = 1
colCount = int(len(testingSets))
for testResultFname in testResultFiles:
    #parse training & testing set names
    splittedTRLFname = os.path.basename(testResultFname).split(".")
    trnSet = str(splittedTRLFname[0].split("_")[0])+"trn"
    tstSet = str(splittedTRLFname[2].split("_")[0])+"tst"
    print "trnSet: ",trnSet,"\t",
    print "tstSet: ",tstSet


    testResInStream = None
    try:
        testResInStream = open(testResultFname,"r")
    except:
        print "Error Opening test result file: ",testResultFname
        exit(0)
    
    testResLines = testResInStream.readlines()
    tRLIndex = 0
    for testResLine in testResLines:
        if '<-- classified as' in testResLine:
            break
        tRLIndex+=1
    #print "\n"
    #print testResLines[tRLIndex]
    #print testResLines[tRLIndex+1]
    #print testResLines[tRLIndex+2]

    #get false positives
    splittedTRL = testResLines[tRLIndex+1].split()
    FP = (float(splittedTRL[1])/(float(splittedTRL[0])+float(splittedTRL[1])))*100
    FPStr = round(FP,4)
    #get false negative
    splittedTRL = testResLines[tRLIndex+2].split()
    FN = (float(splittedTRL[0])/(float(splittedTRL[0])+float(splittedTRL[1])))*100
    FNStr = round(FN,4)
    
    print "FP:", FP,FPStr,"\t",
    print "FN:", FN,FNStr,"\n"
    
    if col ==1:
        wsfp.write(row, 0, trnSet)
        wsfn.write(row, 0, trnSet)
    if row ==1:
        wsfp.write(0, col, tstSet)
        wsfn.write(0, col, tstSet)
    wsfp.write(row, col, FPStr)
    wsfn.write(row, col, FNStr)
    col+=1
    if col == colCount+1:
        col = 1
        row+=1
    

#Get number of bots needed
col = 1 #since col 0 is already written
row = 1
colCount = int(len(testingSets))
#intilize row, col for minMBNPra details
minMBDetRow = 1
minMBDetCol = 0

for misclassificationFname in misclassificationFiles:
    #parse training & testing set names
    splittedMRLFname = os.path.basename(misclassificationFname).split(".")
    trnSet = str(splittedMRLFname[0].split("_")[0])+"trn"
    tstSet = str(splittedMRLFname[2].split("_")[0])+"tst"
    print "trnSet: ",trnSet,"\t",
    print "tstSet: ",tstSet


    misClsficResInStream = None
    try:
        misClsficResInStream = open(misclassificationFname,"r")
    except:
        print "Error Opening test result file: ",misclassificationFname
        exit(0)
    
    misClsficResLines = misClsficResInStream.readlines()
    minMB = "INF" # will store the minimum botnet size
    # will keep track of NPra parameters for the bot with min botnet size
    minMBNPra = None     

    for misClsficResLine in misClsficResLines:
        #parse line
        if 'ATTACKER' in misClsficResLine:
            splittedMRL = misClsficResLine.split()
            if 'ATTACKER' in splittedMRL[1] and 'USER' in splittedMRL[2]:
                #print splittedMRL
                NPraList = splittedMRL[5].split("(")[1].split(")")[0].split(",")
                print NPraList
                MB = getMinimumBotnetSize(NPraList)
                #print "MB1=",MB
                if minMB is "INF" or ((MB is not "INF") and (int(MB) < int(minMB))):
                    minMB = MB
                    minMBNPra = NPraList

    print "minMB=",minMB
    if col ==1:
        wsbotcount.write(row, 0, trnSet)
    if row ==1:
        wsbotcount.write(0, col, tstSet)
    wsbotcount.write(row, col, str(minMB))

    #write NPra for the minMB bot
    wsMinMBDetails.write(minMBDetRow,minMBDetCol,trnSet);
    wsMinMBDetails.write(minMBDetRow,minMBDetCol+1,tstSet);
    wsMinMBDetails.write(minMBDetRow,minMBDetCol+2,minMB);
    wsMinMBDetails.write(minMBDetRow,minMBDetCol+3,str(minMBNPra));
    
    minMBDetRow += 1
    minMBDetCol = 0

    col+=1
    if col == colCount+1:
        col = 1
        row+=1
try:    
    #wb.save('report.xls')
    wb.save(os.path.join(args.outdir,os.path.basename('reports.xls')))
except Exception as e:
    print e.args
    print e
