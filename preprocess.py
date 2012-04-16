"""
Program to preprocess the dataset which includes following
    1. filter out requests from robots
"""
from pyparsing import alphas,nums, dblQuotedString, Combine, Word, Group, \
                        delimitedList, Suppress, removeQuotes

from progressbar import ProgressBar , Percentage, Bar
from urlparse import urlparse
import urllib
import string,datetime,time,pyparsing
import argparse
import os, sys,math
import re
import UserAgentType as UAT

indnt = "  "
indntlevel = 0
invalidFormatCount = 0;
validRequestCount = 0;
totalLogCount = 0
robotCount = 0


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
                        setResultsName("numBytesSent")+\
                    (dblQuotedString | "-").\
                        setResultsName("redirectURL")+\
                    (dblQuotedString | "-").\
                        setResultsName("userAgent").\
                        setParseAction(self.userAgentParser)
                    )
        return logLine

    def parseLogLine(self,line):
        return self.parser.parseString(line)
        
        


# parse commandline arguments
def parseCmdArgs():
    desc = "preprocess to the dataset: filter robots"
    parser = argparse.ArgumentParser(description=desc,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                add_help=False)
    parser.add_argument("-h", "--help", action="help",
            help="Show this help message and exit")
    parser.add_argument("-i", "--apache-log-file", required=True,
            help="Apache Log File")
    parser.add_argument("-o", "--outfile", required = True,
            help="Output filter")
    args = parser.parse_args()
    return args

#parse commandlist arguments    
args = parseCmdArgs()
outputStream = None
try:
    outputStream = open(args.outfile,"w")
except:
    print "Error Opening output file: ",args.outfile
    exit(0)
#stats filename
statsFname = args.outfile+"_stats"
statsOutputStream = None
try:
    statsOutputStream = open(statsFname,"w")
except:
    print "Error Opening stats output file: ",statsFname
    exit(0)
#create useragenttype object
userAgentTypeObject = UAT.UserAgentType()
alp = ApacheLogParser()

try: 
    f = open(args.apache_log_file)
except:
    print "Apache Log File Open Error"
    exit(0)
#with open(sys.argv[1]) as f:
print "preprocessing: ",args.apache_log_file

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
    totalLogCount +=1
    try:    
        parsedLogLine = alp.parseLogLine(line)
        #print dir(parsedLogLine)
        #print parsedLogLine
        #print parsedLogLine.ipAddr, parsedLogLine.timestamp,\
            #parsedLogLine.requestURI
      

        #check if the user agent is browser type(not robot,crawler etc)
        userAgent = parsedLogLine.userAgent
        if userAgentTypeObject.isRobot(userAgent):
            robotCount +=1
        else:
            validRequestCount +=1
            outputStream.write(line)
        
                  
    except pyparsing.ParseException, err:
        """
        print "invalid log format:"
        print "  ", err.line
        print "  "," "*(err.column-1) + "^"
        print "  ",err
        """
        validRequestCount +=1
        outputStream.write(line)
        
    #except ValueError:
    #   print "parsing failed"
    #   print "  ","line: ", line
print "validRequestCount",validRequestCount
print "totalLogCount",totalLogCount
print "robotCount",robotCount
statsOutputStream.write("totalLogCount::"+str(totalLogCount)+"\n") 
statsOutputStream.write("validRequestCount::"+str(validRequestCount)+"\n") 
statsOutputStream.write("robotCount::"+str(robotCount)+"\n") 
