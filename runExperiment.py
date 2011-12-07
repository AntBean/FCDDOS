import os,sys,argparse,pickle
# parse commandline arguments
def parseCmdArgs():
    desc = "runExperiment for request dynamics model"
    parser = argparse.ArgumentParser(description=desc,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                add_help=False)
    parser.add_argument("-h", "--help", action="help",
            help="Show this help message and exit")
    parser.add_argument("-u", "--unparsed-log-file",
            help="Unparsed Apache Log File")
    parser.add_argument("-p", "--parsed-log-file",
            help="Unparsed Apache Log File")
    parser.add_argument("-o", "--outdir", default=None, required = True,
            help="Output Directory")
    args = parser.parse_args()
    return args


#parse commandlist arguments    
args = parseCmdArgs()

if (args.unparsed_log_file is None) and (args.parsed_log_file is None):
    print "Atleast one of them is needed: unparsed log file or parsed log file"
if args.unparsed_log_file:
    args.parsed_log_file = os.path.join(args.outdir,os.path.basename(args.unparsed_log_file)+
                                        "_u"
            )
    parseApacheCommand = "python parseApacheLog.py -i "+args.unparsed_log_file+\
                            " -o "+args.outdir
    print "parsed out file: ",args.parsed_log_file
    print "Parse apache command: ", parseApacheCommand
    os.system(parseApacheCommand)

statsFname = args.parsed_log_file+"_pickle"
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
minP1 = outStats[2]
maxP1 = outStats[3]
minr1 = outStats[4]
maxr1 = outStats[5]
mina1 = outStats[6]
maxa1 = outStats[7]
TotalNumberUser = outStats[8]
TotalNumberReq = outStats[9]

attackerOutFname = str(args.parsed_log_file.partition("_u")[0])+"_a"
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
                        args.parsed_log_file+\
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
userTrFname = args.parsed_log_file+"_tr"
attackerTrFname = attackerOutFname+"_tr"
mixTrCmd = "python mix_user_attacker.py -u "+userTrFname+\
            " -a "+attackerTrFname+\
            " -f arffFormat"
print "mixTrCmd", mixTrCmd
os.system(mixTrCmd)
#mix user & attacker testing set
userTeFname = args.parsed_log_file+"_te"
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
