import os,sys,argparse,pickle
import math, xlwt
from RequestSemanticModel import writeSequencesProbToFile
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
        parseApacheCommand = "python parseApacheLog.py -i "+unparsed_log_file+\
                            " -o "+args.outdir
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
statsRowIndx = 1

#most aggressive attacker parameter
minN1Agg = None
maxN1Agg = None
minP1Agg = None
maxP1Agg = None
minr1Agg = None
maxr1Agg = None
mina1Agg = None
maxa1Agg = None

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
    #set most aggressive attacker parameters
    if minN1Agg is None:
        minN1Agg = outStats[0]
    elif minN1Agg > outStats[0]:
        minN1Agg = outStats[0]
    else:
        None

    if maxN1Agg is None:
        maxN1Agg = outStats[1]
    elif maxN1Agg < outStats[1]:
        maxN1Agg = outStats[1]
    else:
        None
    
    if minP1Agg is None:
        minP1Agg = outStats[2]
    elif minP1Agg > outStats[2]:
        minP1Agg = outStats[2]
    else:
        None

    if maxP1Agg is None:
        maxP1Agg = outStats[3]
    elif maxP1Agg < outStats[3]:
        maxP1Agg = outStats[3]
    else:
        None
    
    if minr1Agg is None:
        minr1Agg = outStats[4]
    elif minr1Agg > outStats[4]:
        minr1Agg = outStats[4]
    else:
        None

    if maxr1Agg is None:
        maxr1Agg = outStats[5]
    elif maxr1Agg < outStats[5]:
        maxr1Agg = outStats[5]
    else:
        None
    
    if mina1Agg is None:
        mina1Agg = outStats[6]
    elif mina1Agg > outStats[6]:
        mina1Agg = outStats[6]
    else:
        None

    if maxa1Agg is None:
        maxa1Agg = outStats[7]
    elif maxa1Agg < outStats[7]:
        maxa1Agg = outStats[7]
    else:
        None

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
    """
    minN1 = outStats[0]
    maxN1 = outStats[1]
    minP1 = str(round(outStats[2],2))
    maxP1 = str(round(outStats[3],2))
    minr1 = str(round(outStats[4],2))
    maxr1 = str(round(outStats[5],2))
    mina1 = str(round(outStats[6],2))
    maxa1 = str(round(outStats[7],2))
    """
    minN1 = minN1Agg
    maxN1 = maxN1Agg
    minP1 = str(round(minP1Agg,2))
    maxP1 = str(round(maxP1Agg,2))
    minr1 = str(round(minr1Agg,2))
    maxr1 = str(round(maxr1Agg,2))
    mina1 = str(round(mina1Agg,2))
    maxa1 = str(round(maxa1Agg,2))
    
    TotalNumberUser = outStats[8]
    TotalNumberAttacker = outStats[9]
    TotalNumberReq = outStats[10]
    invalidFormatCount = outStats[11]
    invalidNPraCount = outStats[12]
    totalLogCount = outStats[13]
    fileExtnAccessFrequencyTable = outStats[14]
    sequences = outStats[15]
    requestGraph = outStats[16]
    fileSequences = outStats[17]
    fileRequestGraph = outStats[18]

    #update TotalNumberOfAttacker
    TotalNumberAttacker = (TotalNumberAttacker * int(args.attacker_user_ratio))
    
    ID = str(os.path.basename(parsed_log_file).partition("_u")[0])
    #write stats data to report file
    wsstats.write(statsRowIndx, 0, ID)
    wsstats.write(statsRowIndx, 1, TotalNumberUser)
    wsstats.write(statsRowIndx, 2, TotalNumberAttacker)
    wsstats.write(statsRowIndx, 3, TotalNumberReq)
    wsstats.write(statsRowIndx, 4, invalidFormatCount)
    wsstats.write(statsRowIndx, 5, invalidNPraCount)
    wsstats.write(statsRowIndx, 6, totalLogCount)
    wsstats.write(statsRowIndx, 8, "["+str(minN1)+"-"+str(maxN1)+"]")
    wsstats.write(statsRowIndx, 9, "["+str(minP1)+"-"+str(maxP1)+"]")
    wsstats.write(statsRowIndx, 10, "["+str(minr1)+"-"+str(maxr1)+"]")
    wsstats.write(statsRowIndx, 11, "["+str(mina1)+"-"+str(maxa1)+"]")
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

    #write dir sequence probability data to the report file
    wsSequencesProbRow = 1
    for sequence in sequences:
        wsSequencesProb.write(wsSequencesProbRow,0,sequence.getId())
        wsSequencesProb.write(wsSequencesProbRow,1,sequence.getSequenceProb())
        wsSequencesProb.write(wsSequencesProbRow,2,sequence.getSequenceLength())
        wsSequencesProbRow += 1
    #write sequence probability data to the text Log file
    sequenceProbOutFname = str(outBaseFname.partition("_u")[0])+".SequenceProb"
    writeSequencesProbToFile(sequences,sequenceProbOutFname)
    
    #write file sequence probability data to the report file
    wsFileSequencesProbRow = 1
    for fileSequence in fileSequences:
        wsFileSequencesProb.write(wsFileSequencesProbRow,0,\
                fileSequence.getId())
        wsFileSequencesProb.write(wsFileSequencesProbRow,1,\
                fileSequence.getSequenceProb())
        wsFileSequencesProb.write(wsFileSequencesProbRow,2,\
                fileSequence.getSequenceLength())
        wsFileSequencesProbRow += 1
    #write fileSequence probability data to the text Log file
    fileSequenceProbOutFname = str(outBaseFname.partition("_u")[0])+".FileSequenceProb"
    writeSequencesProbToFile(fileSequences,fileSequenceProbOutFname)

        

    #attackerOutFname = str(parsed_log_file.partition("_u")[0])+"_a"
    attackerOutFname = str(outBaseFname.partition("_u")[0])+"_a"
    #run attack_generate command
    attackGenerateCmd ="python attack_generate.py -o "+attackerOutFname+\
                        " -n "+str(TotalNumberAttacker)+\
                        " -N "+str(minN1)+"-"+str(maxN1)+\
                        " -P "+str(minP1)+"-"+str(maxP1)+\
                        " -r "+str(minr1)+"-"+str(maxr1)+\
                        " -a "+str(mina1)+"-"+str(maxa1)
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
    generateModelCmd = "java weka.classifiers.trees.J48 -t "+trFname+\
                   " -d "+modelFname+\
                   " > "+trResultsFname
    print "trFname: ",trFname
    print "modelFname: ",modelFname
    print "trResultsFname: ",trResultsFname
    print "generateModelCmd: ",generateModelCmd
    os.system(envVar)
    os.system(generateModelCmd)
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
        testCmd = "java weka.classifiers.trees.J48"+\
                    " -T "+testSet+" -l "+model+\
                    " -i > "+testResultFname
        print testCmd
        os.system(testCmd)
        misclassificationFname =  model+"."+str(os.path.basename(testSet))+\
                                    ".misclassfication"
        misclassificationFiles.append(misclassificationFname)
        misclassificationCmd = "java weka.classifiers.trees.J48"+\
                                " -T "+testSet+\
                                " -l "+model+" -i -p 1-16 | grep '+' > "+\
                                misclassificationFname
        print misclassificationCmd
        os.system(misclassificationCmd)

#generate report
wsfp.write(0, 0, "FP")
wsfn.write(0, 0, "FN")
wsbotcount.write(0,0,"#BotsNeeded")

#Get FP and FN
col = 1 #since col 0 is already written
row = 1
colCount = int(math.sqrt(len(testResultFiles)))
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
colCount = int(math.sqrt(len(misclassificationFiles)))
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
    minMB = None # will store the minimum botnet size
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
                N=float(NPraList[0])
                P=float(NPraList[1])
                r=float(NPraList[2])
                a=float(NPraList[3])
                Pt = (P*(N-1))
                #MB = int(1000*(a+P/r)*(600/(Pt*(N-1)+N*r*a)))
                """
                This should be the correct calculation as P*(N-1) will give the 
                sum of all the pauses between searching session, so again we don't need
                to multiply Pt with N-1
                """
                MB = int(1000*(a+P/r)*(600/(P*(N-1)+N*r*a)))
                print "MB1=",MB
                if minMB is None or MB < minMB:
                    minMB = MB
                    minMBNPra = NPraList

    print "minMB=",minMB
    if col ==1:
        wsbotcount.write(row, 0, trnSet)
    if row ==1:
        wsbotcount.write(0, col, tstSet)
    if minMB is None:
        wsbotcount.write(row, col, "INF")
    else:
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
