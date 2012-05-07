"""
type = 0 int to str mapping
type = 1 int to str mapping
"""

class RequestMapper:

    def __init__(self):
        self.dirMap = {}
        self.fileMap = {}
        self.fileToDirMap = {}
        self.dirIntValue = 0
        self.fileIntValue = 0

    def getDirInt(self,dirStr):
        outInt = None
        for key,value in self.dirMap.iteritems():
            if value == dirStr:
                outInt = key
                break
        return outInt

    def getDirStr(self,dirInt):
        if self.dirMap.has_key(dirInt):
            return self.dirMap[dirInt]
        else:
            return None
    
    def getFileInt(self,fileStr):
        outInt = None
        for key,value in self.fileMap.iteritems():
            if value == fileStr:
                outInt = key
                break
        return outInt

    def getFileStr(self,fileInt):
        if self.fileMap.has_key(fileInt):
            return self.fileMap[fileInt]
        else:
            return None
    
    def getDirIntFromFileInt(self,fileInt):
        if self.fileToDirMap.has_key(fileInt):
            return self.fileToDirMap[fileInt]
        else:
            return None

    def getAllFileInt(self):
        return [fileInt for fileInt in self.fileMap.keys()]

    def getAllDirInt(self):
        return [dirInt for dirInt in self.dirMap.keys()]

    """
    if there is no mapping for request then a new mapping is created
        and new mapping will be returned
    else
        existing mapping will be returned 
    request should be in char form
    """
    def setMapping(self,fileStr,dirStr):
        fileInt = None
        dirInt = None
        #check if there exist a mapping for fileStr
        fileInt = self.getFileInt(fileStr) 
        if fileInt == None:
            self.fileMap[self.fileIntValue]= fileStr
            fileInt = self.fileIntValue
            self.fileIntValue +=1
        
        #check if there exist a mapping for dirStr
        dirInt = self.getDirInt(dirStr) 
        if dirInt == None:
            self.dirMap[self.dirIntValue]= dirStr
            dirInt = self.dirIntValue
            self.dirIntValue +=1
        
        #check if there exist a mapping for fileInt to dirInt
        if self.getDirIntFromFileInt(fileInt) == None:
            self.fileToDirMap[fileInt]= dirInt

        return fileInt,dirInt

    def showFileMap(self):
        print "####################File Map Start############"
        for fileInt,fileStr in self.fileMap.iteritems():
            print "mapping:",fileInt,"->",fileStr
        print "####################File Map End##############"
    
    def showDirMap(self):
        print "####################Dir Map Start############"
        for dirInt,dirStr in self.dirMap.iteritems():
            print "mapping:",dirInt,"->",dirStr
        print "####################Dir Map End##############"
    
    def showFileToDirMap(self):
        print "####################File To Dir Map Start############"
        for fileInt,dirInt in self.fileToDirMap.iteritems():
            print "mapping:",self.getFileStr(fileInt),"->",self.getDirStr(dirInt)
        print "####################File To Dir Map End##############"

"""
sampleData = {}
sampleData['/home/123.html'] = '/home/'
sampleData['/home/222.html'] = '/home/'
sampleData['/home/444.html'] = '/home/'
sampleData['/home/222.html'] = '/home/'
sampleData['/home/444.html'] = '/home/'
sampleData['/test/cool.html'] = '/test/'
sampleData['/test/doom.html'] = '/test/'
sampleData['/test/cool.html'] = '/test/'
rmap  = RequestMapper()

for fileStr,dirStr in sampleData.iteritems():
    rmap.setMapping(fileStr,dirStr)

rmap.showFileMap()
rmap.showDirMap()
rmap.showFileToDirMap()

print rmap.getAllFileInt()
print rmap.getAllDirInt()
"""
