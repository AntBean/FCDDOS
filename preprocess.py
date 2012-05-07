"""
preprocess the robot filtred apache log file and make it 
suitable for creating models data
"""
from pyparsing import alphas,nums, dblQuotedString, Combine, Word, Group, \
                        delimitedList, Suppress, removeQuotes

from progressbar import ProgressBar , Percentage, Bar
from urlparse import urlparse
import urllib
from RequestSemanticModel import *
import string,datetime,time,pyparsing
import argparse
import os, sys,math
import re
import pickle
from FileCategory import fileCategoryNames,fileCategories
import mapper

indnt = "  "
indntlevel = 0

#attacker parameters
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

    def userAgentParser(self,s,l,t):
        userAgent = str(t[0].strip('"'))
        t["userAgent"] = userAgent
    
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
                    dblQuotedString.\
                        setResultsName("cmd").\
                        setParseAction(self.httpCmdParser)+\
                    (integer | "-").\
                        setResultsName("statusCode")+\
                    (integer | "-").\
                        setResultsName("numBytesSent")
                    )
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
 method to get filetype from the request uri
"""
def getFileType(requestURI):
    fileEXTN = getFileEXTN(requestURI)
    for fileCategory in fileCategories:
        if fileEXTN in fileCategory:
            index = fileCategories.index(fileCategory)
            return fileCategoryNames[index]
 
    return "misc"

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
    desc = "parse apache log file(robots filtered) and generate data for models"
    parser = argparse.ArgumentParser(description=desc,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                add_help=False)
    parser.add_argument("-h", "--help", action="help",
            help="Show this help message and exit")
    parser.add_argument("-i", "--apache-log-file", required=True,
            help="Apache robots filterd Log File")
    parser.add_argument("-m", "--request-mapping", required=True,
            help="request mapping pickle file")
    parser.add_argument("-o", "--outdir",required = True,
            help="Output Directory")
    args = parser.parse_args()
    return args


#parse commandlist arguments    
args = parseCmdArgs()
outStatsFname = os.path.join(args.outdir,os.path.basename(args.apache_log_file))
  
# a hash table to keep parsed apache log line as entries 
# with client ip address as the key 
# each hash table enty is a list of request 
# with all the request having the same ip
logHashTable = {}

#hashtable to keep the count of different file extensions
#this will be used to decide which file types should be added for our analysis
fileExtnAccessFrequencyTable = {}

alp = ApacheLogParser()

try: 
    f = open(args.apache_log_file)
except:
    print "Apache Log File Open Error"
    exit(0)

requestMappingStream = None
try:
    requestMappingStream = open(args.request_mapping,"rb")
    requestMapper = pickle.load(requestMappingStream)
except IOError:
    print "Error Opening pickle file: ",args.request_mapping
    print "creating it Now!!"
    requestMappingStream = open(args.request_mapping,"wb")
    requestMapper = mapper.StrToIntMapper()

# get the file size
f.seek(0,2)
fileSize = f.tell()
f.seek(0,0)
# intilize the progress bar
readProgBar = ProgressBar(widgets = [Bar(),Percentage()],\
        maxval=fileSize).start()

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
        
        fileEAFTKey = getFileEXTN(parsedLogLine.requestURI)
            

        #update the counter if key is already present else add the key     
        if fileEAFTKey not in fileExtnAccessFrequencyTable:
            fileExtnAccessFrequencyTable[fileEAFTKey] = 1 
        else:
            fileExtnAccessFrequencyTable[fileEAFTKey]+=1

        #logHashTable[parsedLogLine.ipAddr] = parsedLogLine
        if parsedLogLine.ipAddr not in logHashTable:
            logHashTable[parsedLogLine.ipAddr] = []
        #set the str to int mapping for uri
        requestInt = requestMapper.setMapping(parsedLogLine.requestURI)
        #print "mapping:",requestInt,"->",parsedLogLine.requestURI
        entry = [parsedLogLine.timestamp,requestInt]
        #print "entry ",entry
        logHashTable[parsedLogLine.ipAddr].append(entry)
        
                  
                
            
            
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

print "total log count",totalLogCount
print "invalid format = ", invalidFormatCount
outStats = [invalidFormatCount,totalLogCount,logHashTable,fileExtnAccessFrequencyTable]
pickle.dump(outStats, open(outStatsFname,"wb"))

#update the mappings file
if os.path.isfile(args.request_mapping):
    os.remove(args.request_mapping)
pickle.dump(requestMapper, open(args.request_mapping,"wb"))

#print the mapping
requestMapper.show()
