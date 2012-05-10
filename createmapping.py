from mapper import RequestMapper as RequestMapper
from apachelogparser import ApacheLogParser as ApacheLogParser
from apachelogparser import getSubDir as getSubDir
from  apachelogparser import getFileName as getFileName
from progressbar import ProgressBar , Percentage, Bar

import argparse,os,sys,pyparsing
import pickle

"""
module to create mapping from str to int for file and dir
"""
# parse commandline arguments
def parseCmdArgs():
    desc = "parse apache log files and create mapppings"
    parser = argparse.ArgumentParser(description=desc,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                add_help=False)
    parser.add_argument("-h", "--help", action="help",
            help="Show this help message and exit")
    parser.add_argument("-i", "--apache-log-files", default=None, nargs = '*',
            help="Apache Log File")
    parser.add_argument("-o", "--request-mapping", required=True,
            help="ouput request mapping pickle file")
    args = parser.parse_args()
    return args

#parse commandlist arguments    
args = parseCmdArgs()

alp = ApacheLogParser()
requestMapper = RequestMapper()


for apache_log_file in args.apache_log_files:
    print "###########Mapping for "+apache_log_file+" Starts########"
    try: 
        f = open(apache_log_file)
    except:
        print "Opening Apache Log File: "+apache_log_file+" Error"
        exit(0)


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
        try:    
            parsedLogLine = alp.parseLogLine(line)
            #print dir(parsedLogLine)
            #print parsedLogLine
            #print parsedLogLine.ipAddr, parsedLogLine.timestamp,\
            #parsedLogLine.requestURI
            #getDirName
            dirStr = getSubDir(parsedLogLine.requestURI)
            #getFileName
            fileStr = getFileName(parsedLogLine.requestURI)
            #set mapping file and dir
            fileInt,dirInt = requestMapper.setMapping(fileStr,dirStr)

        except pyparsing.ParseException, err:
            pass
    print "###########Mapping for "+apache_log_file+" Ends##########"

#create mappiing file
pickle.dump(requestMapper, open(args.request_mapping,"wb"))
"""
#print the mapping
requestMapper.showFileMap()
requestMapper.showDirMap()
requestMapper.showFileToDirMap()
"""
