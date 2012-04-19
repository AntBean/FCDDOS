import os,sys

class StrToIntMapper:

    def __init__(self):
        self.strToIntMap = {}
        self.intCounter = 0

    def getStrToIntMapping(self,inStr):
        if self.strToIntMap.has_key(inStr):
            return self.strToIntMap[inStr]
        else:
            print "no mapping exists for string: ",inStr
            return None

    """
    if there is no mapping for request then a new mapping is created
        and new mapping will be returned
    else
        existing mapping will be returned 
    request should be in char form
    """
    def setMapping(self,inStr):
        if not self.strToIntMap.has_key(inStr):
            self.strToIntMap[inStr]=self.intCounter
            self.intCounter +=1
        return self.getStrToIntMapping(inStr)

    def getIntToStrMapping(self,inInt):
        outStr = None
        for key,value in self.strToIntMap.iteritems():
            if value == inInt:
                outStr = key
                break
        if outStr == None:
            print "inInt: ",inInt," not found in the mapping"
        return outStr

    
