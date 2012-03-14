import argparse,os,sys
def parseCmdArgs():
    desc = "parse mis classificaiton"
    parser = argparse.ArgumentParser(description=desc,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                add_help=False)
    parser.add_argument("-h", "--help", action="help",
            help="Show this help message and exit")
    parser.add_argument("-m", "--misclassification", default=None,
            required = True,
            help="misclassification file")
    parser.add_argument("-s", "--seqprob", default=None,
            required = True,
            help="seq probability file file")
    parser.add_argument("-o", "--outfile", default="outfile",
            help="Output file")
    parser.add_argument("-t", "--target", default="Attacker",
            help="search string user or User or Attacker")
    args = parser.parse_args()
    return args


#parse commandlist arguments    
args = parseCmdArgs()
misClsficResInStream = None
try:
    misClsficResInStream = open(args.misclassification,"r")
except:
    print "Error Opening test result file: ",args.misclassification
    exit(0)
misClsficResLines = misClsficResInStream.readlines()

 
seqProbInStream = None
try:
    seqProbInStream = open(args.seqprob,"r")
except:
    print "Error Opening file: ",args.seqprob
    exit(0)
seqProbLines = seqProbInStream.readlines()

outputStream = None
try:
    outputStream = open(args.outfile,"w")
except:
    # happend when the outfile is specified incorrectly 
    # or not specified at all
    outputStream = sys.stdout
outputLines = []
for misClsficResLine in misClsficResLines:
    if args.target in misClsficResLine:
        #print misClsficResLine
        ip = misClsficResLine.split()[0]
        for i in range(len(seqProbLines)):
            seqProbLine = seqProbLines[i]
            if ip in seqProbLine:
                #print seqProbLine
                if seqProbLine in outputLines:
                    continue
                outputLines.append(seqProbLine)
                linesToWrite = int(seqProbLine.split()[2])
                for j in range(linesToWrite+1):
                    #print seqProbLines[i+j]
                    outputStream.write(seqProbLines[i+j])
                #print next lines untill a line with ip comes
