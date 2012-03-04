"""
Assumptions:
    1. if there is only one session of a particular sessiontype is present for user then we will
        use average session pause(parameter P) for that session type as 1 hour
    2. if there is only one request in a session then we don't add gap data(parameter a)
        for that session & if we are not able to find any gap for a session types,     
        then average gap for that session type is set to 1 hour
    3. One entry in the output file contains the parameter for a user
        with request up-to only 1 hour. if there are requests even after 1
        hour from the same user then parameters will calculated for them in new entry.
"""
from pyparsing import alphas,nums, dblQuotedString, Combine, Word, Group, \
                        delimitedList, Suppress, removeQuotes

from progressbar import ProgressBar , Percentage, Bar
from urlparse import urlparse
import urllib
from RequestSemanticModel import *
import string
import datetime
import time
import pyparsing
import argparse
import os, sys
import re
import pickle

indnt = "  "
indntlevel = 0

#attacker parameters
TotalNumberUser = 0
TotalNumberReq = 0
minN1 = None
maxN1 = None
minP1 = None
maxP1 = None
minr1 = None
maxr1 = None
mina1 = None
maxa1 = None
invalidNPraCount = 0
invalidFormatCount = 0;
totalLogCount = 0


class timezone(datetime.tzinfo):
    def __init__(self, name="+0000"):
        self.name = name
        seconds = int(name[:-2])*3600+int(name[-2:])*60
        self.offset = datetime.timedelta(seconds=seconds)

    def utcoffset(self, dt):
        return self.offset

    def dst(self, dt):
        return timedelta(0)

    def tzname(self, dt):
        return self.name

def parse_apache_date(date_str, tz_str):
    # Parse the timestamp from the Apache log file 
    # and return a datetime object
    tt = time.strptime(date_str, "%d/%b/%Y:%H:%M:%S")
    tt = tt[:6] + (0, timezone(tz_str))
    """
        print request[0].day,",",request[0].hour,",",request[0].minute, \
        ",",request[0].second,",",request[0].microsecond
    """
    ts = datetime.datetime(*tt)
    #print ts.isoformat()
    return ts

class ApacheLogParser:
    def __init__(self):
        self.parser = self.prepareParser();

    def httpCmdParser(self,s,l,t):
        httpReqParsed = t[0].strip('"').split()
        method  = httpReqParsed[0]
        requestURI = httpReqParsed[1]
        #decode percentage chars and remove if present with spaces
        requestURI = str(urllib.unquote(requestURI)).split()[0]
        t["method"] = method
        t["requestURI"] = requestURI    
        #t["method"],t["requestURI"],t["protocolVersion"] = \
            #t[0].strip('"').split()
        #t["method"],t["requestURI"] = t.strip('"').split()

    # Takes the timestamp from the apache log and return 
    # a datetime object
    def timestampParser(self,s,l,t):
        TimeStamp = t[0][0]
        TimeZone = t[0][1]
        timestamp = parse_apache_date(TimeStamp,TimeZone)
        t["timestamp"]= timestamp
    
    # intilize the ApacheLogParse with the parsing format
    def prepareParser(self):

        integer = Word( nums )
        ipAddress = delimitedList(Word(alphas+nums+"-_&#"), ".", combine=True)
        #ipAddress = delimitedList(Word(alphas+nums+"-_"), ".", combine=True )
        timeZoneOffset = Word("+-",nums)
        month = Word(string.uppercase, string.lowercase, exact=3)
        
        serverDateTime = Group( Suppress("[") + 
                                Combine( integer + "/" + month + "/" + 
                                            integer + ":" + integer + ":" + 
                                            integer + ":" + integer )+
                                timeZoneOffset + Suppress("]") )
        
        logLine = (ipAddress.setResultsName("ipAddr") +\
                    Suppress("-") +\
                    ("-" | Word( alphas+nums+"@._" )).\
                        setResultsName("auth") +\
                    (serverDateTime | "-" ).\
                        setParseAction(self.timestampParser) +\
                    dblQuotedString.setResultsName("cmd").\
                        setParseAction(self.httpCmdParser) +\
                    (integer | "-").\
                        setResultsName("statusCode")+\
                    (integer | "-").\
                        setResultsName("numBytesSent"))
        return logLine

    def parseLogLine(self,line):
        return self.parser.parseString(line)
        


# will check requestURI to see
# if the request is human-generated
def iSHumanGenerated(URI):
    # list of file names request that will be considered as 
    # human-generated
    fileNames= ["htm","html","shtml","htmf","php","asp","/","pdf"]
    for fname in fileNames:
        regx = fname + "$"
        if re.search(regx,URI):
            return True

    #return True
    return None
# calculate number of sessions 
# for a session type
def calculate_N(sessionType):
    global indntlevel
    indntlevel+=1
    # will check is sessionType is None or Empty
    if not sessionType:
        indntlevel-=1
        return None
    indntlevel-=1
    return len(sessionType)

# calculate average pauses between sessions
# for a session type
def calculate_P(sessionType):
    global indntlevel
    indntlevel+=1
    # will check is sessionType is None or Empty
    if not sessionType:
        indntlevel-=1
        return None
    #print sessionType
    prevSesEndTime = None
    avgPauseList = []
    for session in sessionType:
        #print session
        curSesStartTime = session[0]
        curSesEndTime = session[-1]
        if prevSesEndTime is None:
            # this is the first sesson
            # don't calculate pause time
            #print avgPauseList,curSesStartTime,prevSesEndTime 
            #print session
            prevSesEndTime = curSesEndTime
        else:
            # now calculate pause time
            pauseTime = curSesStartTime-prevSesEndTime
            if pauseTime.total_seconds() < 0:
                return None
            avgPauseList.append(pauseTime.total_seconds())
            #print avgPauseList,curSesStartTime,prevSesEndTime 
            #print session
            prevSesEndTime = curSesEndTime
        
    #exit(0)
    if len(avgPauseList) is 0:
        # generally happens when the session type has only 
        # one session & we need atleast two session 
        # to calculate pause
        # we will set the pause value to be 1 hour in case of only 1 session
        avgPauseList.append(3600)
    #print avgPauseList     
    # return average pause time
    #print float(sum(avgPauseList))/len(avgPauseList)
    indntlevel-=1
    return float(sum(avgPauseList))/len(avgPauseList)

# calculate average number of request
# per session type
def calculate_r(sessionType):
    global indntlevel
    indntlevel+=1
    # will check is sessionType is None or Empty
    if not sessionType:
        indntlevel-=1
        return None
    totNumOfReq = 0
    for session in sessionType:
        totNumOfReq += len(session)
    # return average number of request 
    # for the session type
    #print float(totNumOfReq)/len(sessionType)
    indntlevel-=1
    return float(totNumOfReq)/len(sessionType)

# calculate average request gap in request times
# for a session type
def calculate_a(sessionType):
    global indntlevel
    indntlevel+=1
    # will check is sessionType is None or Empty
    if not sessionType:
        indntlevel-=1
        return None
    # will hold the value of gap between two consecuative 
    # request in a session. we will store gaps for all sessions
    # if there is only one request then we will assume the gap is 3600
    gapList = []
    for session in sessionType:
        prevReq = None
        #only 1 request set gap to 3600
        # dont add gap for this session
        if len(session) > 1:
            for request in session:
                if prevReq is None:
                    prevReq = request
                    continue
                gap = float((request-prevReq).total_seconds())
                if gap < 0:
                    return None
                gapList.append(gap)
                prevReq = request
    if not gapList:
        # generally happens when the session type has only 
        # one session & that session has only one request
        # set the average gap to 3600 for this session type
        gapList.append(3600)
    #print gapList
        
    # return average gap between request in 
    # sessions for this session type
    #print float(sum(gapList))/len(gapList)
    indntlevel-=1
    if sum(gapList) < 0:
        print "mal:",gapList
    return float(sum(gapList))/len(gapList)

    
        
# evaluate N,P,r,a parameters for the 1 session type
# and return a list having N,P,r,a
def calculateNPra(sessionType):
    global indntlevel
    indntlevel+=1
    NPraList = None
    N = calculate_N(sessionType)
    P = calculate_P(sessionType)
    r = calculate_r(sessionType)
    a = calculate_a(sessionType)
    result = [N,P,r,a]  
    #print indntlevel*indnt,result
    #print indntlevel*indnt,sessionType
    if None in result:
        indntlevel-=1
        return None
    indntlevel-=1
    return result
# this function will calculate N,P,ra for each session type
# and will return a list of these parameters
def calculate16Parameters(sessionTypes):
    global indntlevel
    indntlevel+=1
    paramList = []
    i =0
    for j in range(len(sessionTypes)):
        result = calculateNPra(sessionTypes[j])
        #print "i=", i
        if result is None:
            #print len(sessionTypes[j])
            #print indntlevel*indnt,sessionTypes[j]
            #print indntlevel*indnt,sessionTypes
            indntlevel-=1
            return None
        paramList.extend(result)
        #if i ==3:
        #    print sessionTypes[j]
            #exit(0)
        i+=1;
    indntlevel-=1
    return paramList
    
            
def setAttackerParameters(NPraList,R):
    #attacker parameters
    global TotalNumberUser
    global TotalNumberReq
    global minN1
    global maxN1
    global minP1
    global maxP1
    global minr1
    global maxr1
    global mina1
    global maxa1

    if (minN1 is None) or (NPraList[0] < minN1):
        minN1 = NPraList[0]
    if (maxN1 is None) or (NPraList[0] > maxN1):
        maxN1 = NPraList[0]
    if (minP1 is None) or (NPraList[1] < minP1):
        minP1 = NPraList[1]
    if (maxP1 is None) or (NPraList[1] > maxP1):
        maxP1 = NPraList[1]
    if (minr1 is None) or (NPraList[2] < minr1):
        minr1 = NPraList[2]
    if (maxr1 is None) or (NPraList[2] > maxr1):
        maxr1 = NPraList[2]
    if (maxa1 is None) or (NPraList[3] < mina1):
        mina1 = NPraList[3]
    if (maxa1 is None) or (NPraList[3] > maxa1):
        maxa1 = NPraList[3]

#evaluate parameters & write to the outputStream
def evaluate(sessionTypes,R,outputStream,key):
    #print len(sessionTypes[0]),len(sessionTypes[1]),\
    #        len(sessionTypes[2]),len(sessionTypes[3])
    """
    print len(sessionTypes[3])
    for sesn in sessionTypes[3]:
        print sesn
    print sessionTypes[3][0]
    """
    # calculate parameters a,N,P,r,R
    NPraList = calculate16Parameters(sessionTypes)
    # if parameters list is empty or None
    # don't add this output and continue to
    # next table entry
    if not NPraList:
        return 0
    for param in NPraList:
        if param < 0:
            print "mal ip",key;
            return 0
    #print logHashTable[key]
    #set attacker data
    setAttackerParameters(NPraList,R)
    # output data
    #print "Final R", R
    outputData = NPraList
    """
    Don't append the number of request field as this may be used
    J4.8 for learning which we do not want
    outputData.append(R)
    """
    # convert list to comma seperated string
    outputString = ",".join([str(round(x,2)) for x in outputData])
    #outputString += "," 
    #outputString += str(key) 
    attckr_rgx = re.compile("^1\.1\.\d+\.\d+")
    isattacker = attckr_rgx.search(str(key),0)
    if isattacker:
        outputString += ",ATTACKER\n" 
    else:
        outputString += ",USER\n" 
    """
    if str(key) == "1.1.1.1": 
        outputString += ",ATTACKER\n" 
    else:
        outputString += ",USER\n" 
    """
    """
    if args.is_attacker:
        outputString += ",ATTACKER\n" 
    else:
        outputString += ",USER\n" 
    """    
    outputStream.write(outputString)
    #print outputData
    return 1

#processEntryLogHashTable
#process a single entyr log hash table that means
# process the request for i ip address and calculates
#NPra for it
def processEntryLogHashTable(logHashTable,key,\
                                requestGraph,sequences,\
                                fileRequestGraph,fileSequences
                                ):
    global invalidNPraCount
    numValidUsers = 0
    
    #following variables will be used in creation of request graph
    parent = None
    child = None
    
    fileParent = None
    fileChild = None


    #create sequence objets
    sequenceId = key
    sequence = Sequence(sequenceId)
    
    fileSequenceId = key
    fileSequence = Sequence(fileSequenceId)
    
    #timestamp = parse_apache_date(logHashTable[key].timestamp.ts,\ 
                    #logHashTable[key].timestamp.tz)
    #timestamp_str = timestamp.isoformat()  
    #print timestamp
    #print logHashTable[key] , "\n\n"
    #print "ip ", key
    
    # we support only four session types
    # index 0 for searching sessions
    # index 1 for browsing sessions
    # index 2 for relaxed sessions
    # index 3 for long sessions
    sessionTypes = [[],[],[],[]]
    sessionType0 = []
    sessionType1 = []
    sessionType2 = []
    sessionType3 = []

    prevReqTs = None
    startTs = None
    # R is total number of request for this user in one session
    R = 0
    #print key
    for request in logHashTable[key]:
        requestURI = request[1]
        """
        print "request: ",request
        print dir(request)
        print "type: ", type(request)
        exit(0)
        """
        
        """
        #print the sub-directory name
        print key,"=",getSubDir(requestURI),\
            ",",getFileEXTN(requestURI)
        """
        #get sub-dir and append it to the sequence
        #and if edge is ready then add to request graph also
        subDir = getSubDir(requestURI)
        #getFileName
        fileName = getFileName(requestURI)

        if parent is None:
            parent = subDir
        else:
            child = subDir
            requestGraph.append(parent,child)
            parent = child
        
        if fileParent is None:
            fileParent = fileName
        else:
            fileChild = fileName
            fileRequestGraph.append(fileParent,fileChild)
            fileParent = fileChild


        #if outputStatus is 1:
        #   print "request size =" , sys.getsizeof(request)
        if prevReqTs is None:
            prevReqTs = request[0]
            startTs = request[0]
        """
            check if the request[0]-startTs > 3600,if yes we assume then user 
            is using the system second time & create a seprate entry in the 
            parsed file for thisnew session
        """
        #totalSesTime = request[0]-startTs
        maxSessionGap = request[0]-prevReqTs
        #if  totalSesTime.total_seconds() > args.max_full_session_time:
        if  maxSessionGap.total_seconds() > args.max_full_session_time:
            # since these are the last session of each type
            # & will not be added at the end of for loop
            # we have to add them here
            #print sessionType3
            sessionTypes[3].append(sessionType3)
            sessionTypes[2].append(sessionType2)
            sessionTypes[1].append(sessionType1)
            sessionTypes[0].append(sessionType0)
            #calculate paramerter for request added till now, write them output
            """
            if evaluate(sessionTypes,R,outputStream,key)==0:
                invalidNPraCount += R;
            """
            #if error return 0, else dont return anything at this point
            resultEvaluate = evaluate(sessionTypes,R,outputStream,key)
            if resultEvaluate ==0:
                return 0
            else:
                numValidUsers += 1
            #reintilize sessionTypes & variables
            sessionTypes = [[],[],[],[]]
            sessionType0 = []
            sessionType1 = []
            sessionType2 = []
            sessionType3 = []

            prevReqTs = request[0]
            startTs = request[0]
            R = 0

            #append the sequences
            sequences.append(sequence)
            fileSequences.append(fileSequence)
            #also reintilize the data for the request graph and sequences            
            parent = None
            child = None
            fileParent = None
            fileChild = None
            sequence = Sequence(sequenceId)
            fileSequence = Sequence(fileSequenceId)

    
        diff = request[0] - prevReqTs
        #if diff.total_seconds() > 600:
        if diff.total_seconds() > args.long_session:
            sessionTypes[3].append(sessionType3)
            #print sessionType3
            sessionType3 = []
        #if diff.total_seconds() > 300:
        if diff.total_seconds() > args.relaxed_session:
            sessionTypes[2].append(sessionType2)
            sessionType2 = []
        #if diff.total_seconds() > 60:
        if diff.total_seconds() > args.browsing_session:
            sessionTypes[1].append(sessionType1)
            sessionType1 = []
        #if diff.total_seconds() > 10:
        if diff.total_seconds() > args.searching_session:
            sessionTypes[0].append(sessionType0)
            sessionType0 = []
        R+=1

        #seconds = (request.timestamp-startTs).seconds+20
        seconds = (request[0]-startTs)
        sessionType0.append(seconds)
        sessionType1.append(seconds)
        sessionType2.append(seconds)
        sessionType3.append(seconds)
        #sessionType0.append(request.timestamp)
        #sessionType1.append(request.timestamp)
        #sessionType2.append(request.timestamp)
        #sessionType3.append(request.timestamp)
        prevReqTs = request[0]
        
        #add request to the sequences
        sequence.append(subDir)
        fileSequence.append(fileName)
   

    # since these are the last session of each type
    # & will not be added at the end of for loop
    # we have to add them here
    #print sessionType3
    sessionTypes[3].append(sessionType3)
    sessionTypes[2].append(sessionType2)
    sessionTypes[1].append(sessionType1)
    sessionTypes[0].append(sessionType0)
    """
    if evaluate(sessionTypes,R,outputStream,key) == 0:
        invalidNPraCount += R;
    """
    # if error return 0, on success return the valid number of instance 
    # of this user
    resultEvaluate = evaluate(sessionTypes,R,outputStream,key)
    if resultEvaluate ==0:
        return 0
    else:
        #add the sequence to the sequences
        sequences.append(sequence)
        fileSequences.append(fileSequence)
        numValidUsers += 1
        return numValidUsers
        
"""
 method to get sub-directory from the request uri
"""
def getSubDir(requestURI):
    parsedURI = urlparse(requestURI)
    """
    instead of using just the dir name of the file in 
    request uri we will use dirname with complete path
    so that /a/b/1.html and /b/2.html will not return same 
    sub dir name
    """
    #subDir = os.path.dirname(parsedURI.path).split('/')[-1]
    subDir = os.path.dirname(parsedURI.path)
    if len(subDir) ==0:
        return '/'
    else:
        return subDir

"""
 method to get filename from the request uri
 this method will return the filename with complete path information
"""
def getFileName(requestURI):
    parsedURI = urlparse(requestURI)
    fileName = os.path.basename(parsedURI.path)
    
    #remove following from fileName if present
    charsToRemove = ["%20","%22"]
    for charToRemove in charsToRemove:
        fileName = fileName.replace(charToRemove,"")
    
    if '.' in fileName:
        #get the file name without extension
        fileName = ".".join([ x for x in fileName.split('.')[:-1]])
        #get the clean file extensions
        fileEXTN = getFileEXTN(requestURI)
        if '/' not in fileEXTN:
            fileName = fileName+"."+fileEXTN

    return os.path.join(os.path.dirname(parsedURI.path),fileName)


"""
    method to get the file extension from the request uri
"""
def getFileEXTN(requestURI):
    parsedURI = urlparse(requestURI)
    fileName = os.path.basename(parsedURI.path)
    if len(fileName) ==0:
        return '/'

    #remove following from fileName if present
    charsToRemove = ["%20","%22"]
    for charToRemove in charsToRemove:
        fileName = fileName.replace(charToRemove,"")
    #partition the chars after % sign and % itself
    #if % is present in the fileName
    fileName = fileName.split("%")[0]
    if '.' not in fileName:
        return 'misc'
    #get the file extension
    fileEXTN = fileName.split('.')[-1]
   
    """
    remove a bug to deocode hex chars or or partition the fileEXTN 
    #paritiion the filename if hex ex:(\x23)  are present
    #fileEXTN = fileName.split("\\x")[0]
    fileEXTN = re.split("\\\\",fileEXTN)[0]
    """
    #remove chars after the delimeter
    delimeters = ["~", "(", ")", ",", "\\"]
    for delimeter in delimeters:
        fileEXTN = fileEXTN.split(delimeter)[0]

    """
    only return extensions which start starts char or digit
    and have only char and digit in them, remove the extra part
    """
    matchResult = re.search("^[\da-zA-Z]+",fileEXTN)
    if matchResult is None:
        fileEXTN = 'misc'
    else:
        fileEXTN = matchResult.group()
    #convert to lowercase
    fileEXTN = fileEXTN.lower()
    return fileEXTN

# parse commandline arguments
def parseCmdArgs():
    desc = "parse apache log file and output parameters N,P,r,a,R"
    parser = argparse.ArgumentParser(description=desc,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                add_help=False)
    parser.add_argument("-h", "--help", action="help",
            help="Show this help message and exit")
    parser.add_argument("-i", "--apache-log-file", required=True,
            help="Apache Log File")
    parser.add_argument("-o", "--outdir", default=None, required = True,
            help="Output Directory")
    parser.add_argument("-s", "--searching-session", type=int, default=10,
            help="Pause interval for Searching Session")
    parser.add_argument("-b", "--browsing-session", type=int, default=60,
            help="Pause interval for Browsing Session")
    parser.add_argument("-r", "--relaxed-session", type=int, default=300,
            help="Pause interval for Relaxed Session")
    parser.add_argument("-l", "--long-session", type=int, default=600,
            help="Pause interval for long Session")
    parser.add_argument("-t", "--max-full-session-time", type=int, \
            default=3600, \
            help="Maximum time for the complete 1 user session")
    parser.add_argument("-a", "--is-attacker", action = 'store_true', \
            default=False, \
            help="is specified only when the input trace is attack")
    args = parser.parse_args()
    return args


#parse commandlist arguments    
args = parseCmdArgs()
outFname = os.path.join(args.outdir,os.path.basename(args.apache_log_file)+
                                        "_u"
            )
outStatsFname = outFname+"_pickle"
outputStream = None
try:
    outputStream = open(outFname,"w")
except:
    print "Error Opening output file: ",outFname
    exit(0)
    
    
# open a temporary file for keeping data
#tempStream = open("tempfile","w")
tempStream = os.tmpfile()
# a hash table to keep parsed apache log line as entries 
# with client ip address as the key 
# each hash table enty is a list of request 
# with all the request having the same ip
logHashTable = {}

#hashtable to keep the count of different file extensions
#this will be used to decide which file types should be added for our analysis
fileExtnAccessFrequencyTable = {}

#Request Graph to hold edge counts and edge transitional probabilities
#here nodes are sub directory names
requestGraph = RequestGraph()
#sequences to hold the request sequences    
sequences = []

#Request Graph to hold edge counts and edge transitional probabilities
#here nodes are file names 
fileRequestGraph = RequestGraph()
#sequences to hold the request sequences    
fileSequences = []


alp = ApacheLogParser()

try: 
    f = open(args.apache_log_file)
except:
    print "Apache Log File Open Error"
    exit(0)
#with open(sys.argv[1]) as f:

# get the file size
f.seek(0,2)
fileSize = f.tell()
f.seek(0,0)
# intilize the progress bar
readProgBar = ProgressBar(widgets = [Bar(),Percentage()],\
        maxval=fileSize).start()

prevRequestTs = None
embeddedObject = False
for line in f:
    #update the progress bar
    readProgBar.update(f.tell())
    if not line: continue
    totalLogCount+=1
    try:    
        parsedLogLine = alp.parseLogLine(line)
        #print dir(parsedLogLine)
        #print parsedLogLine
        #print parsedLogLine.ipAddr, parsedLogLine.timestamp,\
            #parsedLogLine.requestURI
        
        """
        #update the access frequency of file extensions
        if "." not in parsedLogLine.requestURI:
            fileEAFTKey = "/"
        else:
            fileEAFTTempKey = parsedLogLine.requestURI
            EAFTRe='\.[a-zA-Z\d]+[?\s]|\.[a-zA-Z\d]+$'
            try:
                fileEAFTKey=re.findall(EAFTRe,fileEAFTTempKey)
                #check if key is empty, then make it path access file extension
                if len(fileEAFTKey) == 0:
                    fileEAFTKey = "/"
                else:
                    fileEAFTKey = fileEAFTKey[0].strip(".? ")
            except:
                print fileEAFTTempKey  
                exit(0)
            
           """    
        fileEAFTKey = getFileEXTN(parsedLogLine.requestURI)
            

        #update the counter if key is already present else add the key     
        if fileEAFTKey not in fileExtnAccessFrequencyTable:
            fileExtnAccessFrequencyTable[fileEAFTKey] = 1 
        else:
            fileExtnAccessFrequencyTable[fileEAFTKey]+=1
            
        # check if the request is human-generated or not
        # by verifying the requestURI
        if prevRequestTs is None:
            prevRequestTs = parsedLogLine.timestamp
        else:
            diffTs = parsedLogLine.timestamp - prevRequestTs
            if diffTs.total_seconds() < 3:
                embeddedObject = True

            
        if iSHumanGenerated(parsedLogLine.requestURI) or (not embeddedObject):
            # we only add the human generated to the hashtable
            #logHashTable[parsedLogLine.ipAddr] = parsedLogLine
            if parsedLogLine.ipAddr not in logHashTable:
                logHashTable[parsedLogLine.ipAddr] = []
            entry = [parsedLogLine.timestamp,parsedLogLine.requestURI]
            #print "entry ",entry
            logHashTable[parsedLogLine.ipAddr].append(entry)
        
        else:
            #print "requestURI", parsedLogLine.requestURI
            invalidFormatCount+=1
            
    except pyparsing.ParseException, err:
        pass
        #print "invalid log format:"
        #print "  ", err.line
        #print "  "," "*(err.column-1) + "^"
        #print "  ",err
        invalidFormatCount+=1
    #except ValueError:
    #   print "parsing failed"
    #   print "  ","line: ", line

print "MapSize = " , len(logHashTable)
#print "total log count",totalLogCount
#print "invalid format = ", invalidFormatCount
#print "MapSize = " , sys.getsizeof(logHashTable)
# iterate through the hastable &
# for each entry print 17 parameters by 
# grouping the requests
# ip address is the key to logHashTable
#print "Map: ",logHashTable
outputProgBar = ProgressBar(widgets = [Bar('='),Percentage()]\
        ,maxval=len(logHashTable.keys())).start()

outputStatus = 0
for key in logHashTable.keys():

    outputStatus+=1
    outputProgBar.update(outputStatus)
    notInvalidNPra = True
    #process the reqeust for ip address = key
    resultProcessEntryFunc = processEntryLogHashTable(logHashTable,key,\
                                requestGraph,sequences,\
                                fileRequestGraph,fileSequences\
                                )

    if resultProcessEntryFunc == 0:
        # sort the request for this ip address and then call 
        # processEntryLogHashTable function for sorted request
        logHashTable[key].sort()
        # if still there is a error upate the invalidNPra value
        resultProcessEntryFunc = processEntryLogHashTable(logHashTable,key,\
                                requestGraph,sequences,\
                                fileRequestGraph,fileSequences\
                                )
        if resultProcessEntryFunc == 0:
            notInvalidNPra = False
            invalidNPraCount += len(logHashTable[key])
            for req in logHashTable[key]:
                print req
            exit(0)
    #update the total number of valid user & vallid request
    #only if NPra is valid for the user
    if notInvalidNPra:
        TotalNumberUser += resultProcessEntryFunc
        TotalNumberReq += len(logHashTable[key])

"""
print "##################show file sequences starts##################"
showSequences(fileSequences)
print "##################show file sequences ends##################"
"""
#check attack parameter if they are valid or not
#if min and max values are same, then set them appropriote values
if minN1 == maxN1:
        maxN1 += 1
if minP1 == maxP1:
        minP1 = 1
if minr1 == maxr1:
        maxr1 += 1
if mina1 == maxa1:
        mina1 = 1

#display stats and dump them to pickkle file
print "minN1: ",minN1
print "maxN1: ",maxN1
print "minP1: ",minP1
print "maxP1: ",maxP1
print "minr1: ",minr1
print "maxr1: ",maxr1
print "mina1: ",mina1
print "maxa1: ",maxa1
print "TotalNumberUser: ",TotalNumberUser
print "TotalNumberReq: ",TotalNumberReq
print "total log count",totalLogCount
print "invalid format = ", invalidFormatCount
print "invalid NPra = ", invalidNPraCount
print "total Invalid =",invalidFormatCount+invalidNPraCount

TotalNumberAttacker =TotalNumberUser 
outStats = [minN1,maxN1,minP1,maxP1,minr1,maxr1,mina1,maxa1,TotalNumberUser,\
         TotalNumberAttacker,TotalNumberReq,invalidFormatCount,invalidNPraCount,\
         totalLogCount,fileExtnAccessFrequencyTable,sequences,requestGraph,\
         fileSequences,fileRequestGraph]
pickle.dump(outStats, open(outStatsFname,"wb"))

statsFname = os.path.join(args.outdir,os.path.basename(args.apache_log_file)+
                                        "_stats"
                            )


"""
This Code is not needed anymore as we are writing 
data set stats into pickle file, which is getting written 
int xls sheet, so commenting out this piece of code


statsOutStream = None
try:
    statsOutStream = open(statsFname,"w")
except:
    print "Error Opening stats output file: ",statsFname
statsOutString = "minN1: "+str(minN1)+"\n"+\
                    "maxN1: "+str(maxN1)+"\n"+\
                    "minP1: "+str(round(minP1,2))+"\n"+\
                    "maxP1: "+str(round(maxP1,2))+"\n"+\
                    "minr1: "+str(round(minr1,2))+"\n"+\
                    "maxr1: "+str(round(maxr1,2))+"\n"+\
                    "mina1: "+str(round(mina1,2))+"\n"+\
                    "maxa1: "+str(round(maxa1,2))+"\n"+\
                    "TotalNumberUser: "+str((TotalNumberUser))+"\n"+\
                    "Total log count"+str((totalLogCount))+"\n"+\
                    "TotalNumberReq: "+str((TotalNumberReq))+"\n"+\
                    "invalid format = "+str((invalidFormatCount))+"\n"+\
                    "invalid NPra = "+str(invalidNPraCount)+"\n"

statsOutStream.write(statsOutString)
"""
