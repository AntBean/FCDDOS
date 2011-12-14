import os,sys,argparse,pickle
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
    args = parser.parse_args()
    return args


#parse commandlist arguments    
args = parseCmdArgs()
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
for parsed_log_file in args.parsed_log_files:
    statsFname = parsed_log_file+"_pickle"
    print "stats file name: ",statsFname

    pickleStream = None
    try:
        pickleStream = open(statsFname,"rb")
    except:
        print "Error Opening pickle file: ",statsFname
        exit(0)
    outStats = pickle.load(pickleStream)
    print "outStats: ", outStats
    #attacker parameters
    minN1 = outStats[0]
    maxN1 = outStats[1]
    minP1 = str(round(outStats[2],2))
    maxP1 = str(round(outStats[3],2))
    minr1 = str(round(outStats[4],2))
    maxr1 = str(round(outStats[5],2))
    mina1 = str(round(outStats[6],2))
    maxa1 = str(round(outStats[7],2))
    TotalNumberUser = outStats[8]
    TotalNumberReq = outStats[9]

    attackerOutFname = str(parsed_log_file.partition("_u")[0])+"_a"
    #run attack_generate command
    attackGenerateCmd ="python attack_generate.py -o "+attackerOutFname+\
                        " -n "+str(TotalNumberUser)+\
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
    userTrFname = parsed_log_file+"_tr"
    attackerTrFname = attackerOutFname+"_tr"
    mixTrCmd = "python mix_user_attacker.py -u "+userTrFname+\
            " -a "+attackerTrFname+\
            " -f arffFormat"
    print "mixTrCmd", mixTrCmd
    os.system(mixTrCmd)
    #mix user & attacker testing set
    userTeFname = parsed_log_file+"_te"
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

for model in models:
    for testSet in testingSets:
        testResultFname = model+"."+str(os.path.basename(testSet))+".testResults"
        testCmd = "java weka.classifiers.trees.J48"+\
                    " -T "+testSet+" -l "+model+\
                    " -i > "+testResultFname
        print testCmd
        os.system(testCmd)
        misclassificationFname =  model+"."+str(os.path.basename(testSet))+\
                                    ".misclassfication"
        misclassificationCmd = "java weka.classifiers.trees.J48"+\
                                " -T "+testSet+\
                                " -l "+model+" -i -p 1-17 | grep '+' > "+\
                                misclassificationFname
        print misclassificationCmd
        os.system(misclassificationCmd)
                                
