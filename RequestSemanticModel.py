import os, sys, random,numpy
from progressbar import ProgressBar , Percentage, Bar
from collections import defaultdict
from operator import itemgetter

#global variables
MAX_ATTACKER_SEQUENCE_LENGTH = 1000
MIN_ATTACKER_SEQUENCE_LENGTH = 3
FIRST_ATTACKER_IP = "194.0.0.1"
VALID_METHOD_NAMES = ["dir","file","combined1"]
TOTAL_10MINUTE_ATTACK_REQUEST = 600000
MINIMUM_TEST_SEQUENCE_LENGTH = 3

"""
method to write sequeces classification to the text file for the threshold value
"""
def writeSeqClassificationToFile(sequences, fileName,threshold):
    print "#################writeSeqClassificationTofile Started############"
    space = " "
    colWidth = 16
    try:
        seqProbOutStream = open(fileName,"w")
    except:
        print "Error Opening sequence prob output file: ",fileName

    #first write header    
    header = "SequenceId"+colWidth*space+"prediction\n"
    seqProbOutStream.write(header)
    
    # intilize the progress bar
    writeSeqProgBarEndStatus = len(sequences)
    writeSeqProgBarStartStatus = 0
    writeSeqProgBar = ProgressBar(widgets = [Bar(),Percentage()],\
            maxval=writeSeqProgBarEndStatus).start()

    for sequence in sequences:
        sequenceId = str(sequence.getId())
        predictedClass = "User"
        try:
            if sequence.getTestResults()[threshold][0]:
                predictedClass = "Attacker"
        except:
            print sequence.getTestResults()
            raise
        outString = sequenceId+\
                ((len("sequenceId")-len(sequenceId))+colWidth)*space+\
                predictedClass+"\n"

        seqProbOutStream.write(outString)
        #update the progress bar
        writeSeqProgBarStartStatus += 1
        writeSeqProgBar.update(writeSeqProgBarStartStatus)
    print "#################writeSeqClassificationTofile Ended############"

"""
method to write sequeces probabilities to the chart text file
"""
def writeSequencesProbToChartFile(sequences,fileName,isUser=True):
    print "#################writeSeqProbToChartfile Started###############"
    try:
        seqProbOutStream = open(fileName,"w")
    except:
        print "Error Opening sequence prob output file: ",fileName

    #first write header    
    header = "Type,SequenceLength,EdgeCumProb\n"
    seqProbOutStream.write(header)
    
    # intilize the progress bar
    writeSeqProgBarEndStatus = len(sequences)
    writeSeqProgBarStartStatus = 0
    writeSeqProgBar = ProgressBar(widgets = [Bar(),Percentage()],\
            maxval=writeSeqProgBarEndStatus).start()

    for sequence in sequences:
        requestIndex = 0
        for request in sequence.getRequestSequence():
            if requestIndex < 2:
                requestIndex +=1
                continue
            edgeCumProb = str(sequence.getEdgeCumProb(requestIndex))
            curSeqLen = str(requestIndex+1)
            if isUser:
                name = "User"
            else:
                name = "Attacker"
            outString = name+","+curSeqLen+","+edgeCumProb+"\n"
            seqProbOutStream.write(outString)
            requestIndex +=1
            
        #update the progress bar
        writeSeqProgBarStartStatus += 1
        writeSeqProgBar.update(writeSeqProgBarStartStatus)
 

    print "#################writeSeqProbToChartfile Ended###############"

"""
method to write sequeces probabilities to the text file
"""
def writeSequencesProbToFile(sequences, fileName,reqMap,seqType=0):
    print "#################writeSeqProbTofile Started###############"
    space = " "
    colWidth = 16
    try:
        seqProbOutStream = open(fileName,"w")
    except:
        print "Error Opening sequence prob output file: ",fileName

    #first write header    
    header = "SequenceId"+colWidth*space+"SequenceProb"+\
            +colWidth*space+"SequenceLength"\
            +colWidth*space+"EdgeCumProb"\
            +colWidth*space+"EdgeProb"\
            +colWidth*space+"RequestSequence\n"
    seqProbOutStream.write(header)
    
    # intilize the progress bar
    writeSeqProgBarEndStatus = len(sequences)
    writeSeqProgBarStartStatus = 0
    writeSeqProgBar = ProgressBar(widgets = [Bar(),Percentage()],\
            maxval=writeSeqProgBarEndStatus).start()

    for sequence in sequences:
        sequenceId = str(sequence.getId())
        sequenceProb = str(sequence.getSequenceProb())
        sequenceLength = str(sequence.getSequenceLength())
        outString = sequenceId+\
                ((len("SequenceId")-len(sequenceId))+colWidth)*space+\
                sequenceProb+\
                ((len("SequenceProb")-len(sequenceProb))+colWidth)*space+\
                sequenceLength+\
                ((len("SequenceLength")-len(sequenceLength))+colWidth)*space+\
                "\n"

        seqProbOutStream.write(outString)
        #now write request for this sequence
        startPosition = (len(outString))*space
        requestIndex = 0
        for requestInt in sequence.getRequestSequence():
            request = reqMap.getFileStr(requestInt)
            if seqType == 1:
                request = reqMap.getDirStr(requestInt)
            edgeProb = str(sequence.getEdgeProb(requestIndex))
            edgeCumProb = str(sequence.getEdgeCumProb(requestIndex))
            requestOutString = startPosition+\
                    edgeCumProb+\
                    ((len("EdgeCumProb")-len(edgeCumProb))+colWidth)*space+\
                    edgeProb+\
                    ((len("EdgeProb")-len(edgeProb))+colWidth)*space+\
                    str(request)+"\n"
            seqProbOutStream.write(requestOutString)
            requestIndex +=1
            
        #update the progress bar
        writeSeqProgBarStartStatus += 1
        writeSeqProgBar.update(writeSeqProgBarStartStatus)
    print "#################writeSeqProbTofile Ended###############"

"""
method to write attackersequeces probabilities to the text file
"""
def writeAttackerSequencesProbToFile(sequences, fileName,reqMap,seqType=0):
    space = " "
    colWidth = 16
    MAX_ATTACKER_SEQUENCES = 50
    MAX_ATT_SEQ_PER_RANGE = 10

    try:
        seqProbOutStream = open(fileName,"w")
    except:
        print "Error Opening sequence prob output file: ",fileName

    #first write header    
    header = "SequenceId"+colWidth*space+"SequenceProb"+\
            +colWidth*space+"SequenceLength"\
            +colWidth*space+"RequestSequence\n"
    seqProbOutStream.write(header)

    rangeCounts = [0,0,0,0,0]
    numOfAttSeq = 0
    for sequence in sequences:
        sequenceId = str(sequence.getId())
        sequenceProb = str(sequence.getSequenceProb())
        
        if numOfAttSeq >=MAX_ATTACKER_SEQUENCES:
            return
        if rangeCounts[0] < MAX_ATT_SEQ_PER_RANGE and float(sequenceProb) < 0.2:
            rangeCounts[0] += 1
        elif rangeCounts[1] < MAX_ATT_SEQ_PER_RANGE and (\
                float(sequenceProb) >= 0.2 and float(sequenceProb) < 0.4):
            rangeCounts[1] += 1 
        elif rangeCounts[2] < MAX_ATT_SEQ_PER_RANGE and (\
                float(sequenceProb) >= 0.4 and float(sequenceProb) < 0.6):
            rangeCounts[2] += 1
        elif rangeCounts[3] < MAX_ATT_SEQ_PER_RANGE and (\
                float(sequenceProb) >= 0.6 and float(sequenceProb) < 0.8):
            rangeCounts[3] += 1
        elif rangeCounts[2] < MAX_ATT_SEQ_PER_RANGE and (\
                float(sequenceProb) >= 0.8 and float(sequenceProb) < 1.0):
            rangeCounts[4] += 1
        else:
            continue
        numOfAttSeq += 1
        sequenceLength = str(sequence.getSequenceLength())
        outString = sequenceId+\
                ((len("sequenceId")-len(sequenceId))+colWidth)*space+\
                sequenceProb+\
                ((len("sequenceProb")-len(sequenceProb))+colWidth)*space+\
                sequenceLength+\
                ((len("sequenceLength")-len(sequenceLength))+colWidth)*space+\
                "\n"

        seqProbOutStream.write(outString)
        #now write request for this sequence
        startPosition = (len(outString)+4)*space
        for requestInt in sequence.getRequestSequence():
            request = reqMap.getFileStr(requestInt)
            if seqType == 1:
                request = reqMap.getDirStr(requestInt)
            requestOutString = startPosition+str(request)+"\n"
            seqProbOutStream.write(requestOutString)

"""
method to show the sequences
"""
def showSequences(sequences):
    for index in range(len(sequences)):
        sequenceId = sequences[index].getId()
        requestSequence = sequences[index].getRequestSequence()
        """
        print "["+str(sequenceId)+"]="+str(requestSequence)+","+\
                str(sequences[index].getSequenceLength())
        """
        print "["+str(sequenceId)+"]="+\
                str(sequences[index].getSequenceLength())

"""
method to show the sequence probabilites for all the sequences
"""
def showSequencesProb(sequences):
    for index in range(len(sequences)):
        sequenceId = sequences[index].getId()
        sequenceProb = sequences[index].getSequenceProb()
        print "["+str(sequenceId)+"]="+str(sequenceProb)+","+\
                str(sequences[index].getSequenceLength())
"""
method to caculate thresholds
"""
def getThresholds(requestGraph,sequences):
    seqProb = []
    for seq in sequences:
        seq.calculateSequenceProb(requestGraph)
        seqProb.append(round(seq.getSequenceProb(),2))
    return calculateThresholds(seqProb)

"""
method to calculate threshold for combined1 forumula
"""
def getThresholdsCombined1(dirRequestGraph,fileRequestGraph,
        parentDirToFileGraph,sequences,reqMap):
    seqProb = []
    for seq in sequences:
        seq.calculateSequenceProbCombined1(dirRequestGraph, fileRequestGraph,
               parentDirToFileGraph,reqMap)
        seqProb.append(round(seq.getSequenceProb(),2))
    return calculateThresholds(seqProb)

"""
method to calculate 4 thresholds and return them
"""
def calculateThresholds(seqProb):
    thresholds = []
    seqProb.sort()
    #first threshold is the lowest legitimate seq prob means: 0 % FP
    firstThreshold = seqProb[0]
    thresholds.append(firstThreshold)
    #second threshold is when 2% FP
    secondThreshold = seqProb[int((len(seqProb)*2)/100)]
    if secondThreshold not in thresholds:
        thresholds.append(secondThreshold)
    else:
        secondThreshold = findGreaterSeqProb(firstThreshold,seqProb)
        if secondThreshold is not None:
            thresholds.append(secondThreshold)
    #third threshold is when 3% FP
    thirdThreshold = seqProb[int((len(seqProb)*2)/100)]
    if thirdThreshold not in thresholds:
        thresholds.append(thirdThreshold)
    else:
        thirdThreshold = findGreaterSeqProb(secondThreshold,seqProb)
        if thirdThreshold is not None:
            thresholds.append(thirdThreshold)
    #fourth threshold is when 5% FP
    fourthThreshold = seqProb[int((len(seqProb)*2)/100)]
    if fourthThreshold not in thresholds:
        thresholds.append(fourthThreshold)
    else:
        fourthThreshold = findGreaterSeqProb(thirdThreshold,seqProb)
        if fourthThreshold is not None:
            thresholds.append(fourthThreshold)
    thresholds.sort()
    return thresholds

"""
method to find a seq prob inSeqProb from sorted seqProb list
"""
def findGreaterSeqProb(inSeqProb,seqProbList):
    for seqProb in seqProbList:
        if seqProb > inSeqProb:
            return seqProb
    return None
"""
method to test user and attacker sequences
"""
def testSequences(requestGraph,userSequences,attackerSequences,thresholds):
    # intilize the progress bar
    print "###################testSequences Started######################"
    testSeqProgBarEndStatus = len(userSequences)+len(attackerSequences)
    testSeqProgBarStartStatus = 0
    testSeqProgBar = ProgressBar(widgets = [Bar(),Percentage()],\
            maxval=testSeqProgBarEndStatus).start()

    for seq in userSequences:
        seq.testSequence(requestGraph,thresholds)
        #update the progress bar
        testSeqProgBarStartStatus += 1
        testSeqProgBar.update(testSeqProgBarStartStatus)
        
    for seq in attackerSequences:
        seq.testSequence(requestGraph,thresholds)   
        #update the progress bar
        testSeqProgBarStartStatus += 1
        testSeqProgBar.update(testSeqProgBarStartStatus)
    print "###################testSequences Ended######################"
    return analyzeSequences(userSequences,attackerSequences,thresholds)

"""
method to test user and attacker sequences using combined1
"""
def testSequencesCombined1(dirRequestGraph,fileRequestGraph,\
        parentDirToFileGraph,userSequences,attackerSequences,thresholds,reqMap):
    # intilize the progress bar
    print "#################testSequencesCombined1 Started#############"
    testSeqProgBarEndStatus = len(userSequences)+len(attackerSequences)
    testSeqProgBarStartStatus = 0
    testSeqProgBar = ProgressBar(widgets = [Bar(),Percentage()],\
            maxval=testSeqProgBarEndStatus).start()
    for seq in userSequences:
        seq.testSequenceCombined1(dirRequestGraph,fileRequestGraph,\
                parentDirToFileGraph,thresholds,reqMap)
        #update the progress bar
        testSeqProgBarStartStatus += 1
        testSeqProgBar.update(testSeqProgBarStartStatus)
    for seq in attackerSequences:
        seq.testSequenceCombined1(dirRequestGraph,fileRequestGraph,\
                parentDirToFileGraph,thresholds,reqMap)   
        #update the progress bar
        testSeqProgBarStartStatus += 1
        testSeqProgBar.update(testSeqProgBarStartStatus)
    print "#################testSequencesCombined1 Ended#############"
    return analyzeSequences(userSequences,attackerSequences,thresholds)

"""
method to analyze sequences and return FP,FN,MB
"""
def analyzeSequences(userSequences,attackerSequences,thresholds):
    FP = {}  #false positive
    FN = {}  #false negative
    MB = {} #minimum botnet size

    #get mis detected users
    userMisDetected = defaultdict(int)
    for seq in userSequences:
        testResults = seq.getTestResults()
        for threshold in thresholds:
            if testResults[threshold][0]  == True:
                userMisDetected[threshold] += 1
    #calculate false positives
    """
    print "FP:"
    print userMisDetected
    """
    for threshold in thresholds:
        FP[threshold] = float(str(round((float(userMisDetected[threshold])/\
                    len(userSequences)),6)))  
        """
        print "     ",threshold,FP[threshold],userMisDetected[threshold],\
            len(userSequences)
        """

    #get mis detected attacker
    attackerMisDetected = defaultdict(int)
    for seq in attackerSequences:
        testResults = seq.getTestResults()
        for threshold in thresholds:
            if testResults[threshold][0]  == False:
                attackerMisDetected[threshold] += 1
            minBotSeqLen = testResults[threshold][1]
            minBotSize = TOTAL_10MINUTE_ATTACK_REQUEST/(\
                    minBotSeqLen)
            if MB.has_key(threshold):
                if minBotSize < MB[threshold][0]: 
                    MB[threshold] = [minBotSize,seq.getId(),minBotSeqLen]
            else:
                MB[threshold] = [minBotSize,seq.getId(),minBotSeqLen]
    #calculate false negatives
    """
    print "FN:"
    """
    for threshold in thresholds:
        FN[threshold] = float(str(round((float(attackerMisDetected[threshold])/\
                    len(attackerSequences)),6)))  
        """
        print "     ",threshold,FN[threshold],attackerMisDetected[threshold],\
            len(attackerSequences)
        """
    """
    print "MB:"
    for threshold in thresholds:
        print "     ",threshold,MB[threshold][0],threshold,MB[threshold][1]
    """

    return [FP,FN,MB]

    

class Sequence:
    def __init__(self,seqId):
        self.requestSequence = []
        self.edgeProbs = []
        self.edgeCumProbs = []
        self.sequenceId = seqId
        self.sequenceProb = 0
        self.thresholds = None
        self.testResults = None

    """
    method to return the edge probability 
    """
    def getEdgeProb(self,index):
        return str(round(self.edgeProbs[index],6))
    """
    method to return the edge cum probability 
    """
    def getEdgeCumProb(self,index):
        return str(round(self.edgeCumProbs[index],6))

    """
    method to return the length of the sequences or number of request in it
    """
    def getSequenceLength(self):
        return len(self.requestSequence)
    """
    method to append a request to the sequence
    Note: request in our case is the sub-directory name
    """
    def append(self,request):
        self.requestSequence.append(request)

    """
    method to calculate the sequence probability for this sequence
    using request graph with edge transitional probabilities information
    """
    def calculateSequenceProb(self,requestGraph,isUser=True):
        requestSequence = self.getRequestSequence()
        """
        to save processing do this at end of this funtion
        self.setSequenceProb(requestGraph.getSequenceProb(
                    requestSequence))
        """
        """
        find the probabilities for first request and each edge in 
        in request sequences
        """
        sequence = requestSequence
        firstNodeVisitedProb = float(requestGraph.getNodeVisitedProb(
                    sequence[0])) 
        edgeTP = firstNodeVisitedProb
        self.edgeProbs.append(edgeTP)
        edgeCumProb = float(sum(self.edgeProbs))/len(self.edgeProbs)
        if isUser:
            self.edgeCumProbs.append(edgeCumProb)
        
        for i in range(len(sequence)-1):
            parent = sequence[i]
            child = sequence[i+1]
            edgeTP = requestGraph.getEdgeTransitionalProb(
                    parent,child)
            
            self.edgeProbs.append(float(edgeTP))
            edgeCumProb = float(sum(self.edgeProbs))/len(self.edgeProbs)
            if isUser:
                self.edgeCumProbs.append(edgeCumProb)

        self.setSequenceProb((float(sum(self.edgeProbs)))/(len(self.edgeProbs)))
        if not isUser:
            del self.edgeProbs[:]
            

    """
    method to calculate combined1 sequences probability using file level as 
    well as directory level information
    sequences must contain file level information
    """
    def calculateSequenceProbCombined1(self,dirRequestGraph,fileRequestGraph,
            parentDirToFileGraph,reqMap,isUser=True):
        requestSequence = self.getRequestSequence()
        """
        to save processing do this at end of this funtion
        self.setSequenceProb(fileRequestGraph.getSequenceProbCombined1(\
                    requestSequence,dirRequestGraph,parentDirToFileGraph))
        """
        """
        find the probabilities for first request and each edge in 
        in request sequences
        """
        sequence = requestSequence
        #dirFirstNode = str(str(os.path.dirname(sequence[0])))
        dirFirstNode = reqMap.getDirIntFromFileInt(sequence[0])
        firstNodeVisitedProb = float(fileRequestGraph.getNodeVisitedProb(
                    sequence[0])) 
        if parentDirToFileGraph.isChildTransProbsRoughlyEqual(dirFirstNode):
            firstNodeVisitedProb = float(dirRequestGraph.getNodeVisitedProb(
                        dirFirstNode)) 

        self.edgeProbs.append(firstNodeVisitedProb)
        edgeCumProb = (float(sum(self.edgeProbs)))/(len(self.edgeProbs))
        if isUser:
            self.edgeCumProbs.append(edgeCumProb)
        for i in range(len(sequence)-1):
            parent = sequence[i]
            child = sequence[i+1]

            #get parent,child for dir request graph
            """
            dirParent = str(str(os.path.dirname(parent)))
            dirChild = str(str(os.path.dirname(child)))
            """
            dirParent = reqMap.getDirIntFromFileInt(parent)
            dirChild = reqMap.getDirIntFromFileInt(child)

            edgeTP =fileRequestGraph.getEdgeTransitionalProb(parent,child)  
            dirEdgeTP =dirRequestGraph.getEdgeTransitionalProb(
                    dirParent,dirChild)

            if parentDirToFileGraph.isChildTransProbsRoughlyEqual(dirChild):
                edgeTP = dirEdgeTP

            self.edgeProbs.append(edgeTP)
            edgeCumProb = (float(sum(self.edgeProbs)))/(len(self.edgeProbs))
            self.edgeCumProbs.append(edgeCumProb)

        self.setSequenceProb((float(sum(self.edgeProbs)))/(len(self.edgeProbs)))
        if not isUser:
            del self.edgeProbs[:]

    """
    method to test sequence using threshold using specified method name
    """
    def testSequence(self,requestGraph,thresholds):
        requestSequence = self.getRequestSequence()
        self.setTestResults(requestGraph.testSequence(requestSequence,\
                    thresholds))
    """
    method to test sequence using threshold using specified method name
    and combined1 formula
    """
    def testSequenceCombined1(self,dirRequestGraph,fileRequestGraph,
            parentDirToFileGraph,thresholds,reqMap):
        requestSequence = self.getRequestSequence()
        self.setTestResults(fileRequestGraph.testSequenceCombined1(
                    requestSequence,dirRequestGraph,parentDirToFileGraph,
                    thresholds,reqMap))

    """
       method to set test results
    """
    def setTestResults(self,testResults):
        self.testResults = testResults
    """
    method to get test results for specified method
    """
    def getTestResults(self):
        return self.testResults

    """
    method to return the request sequence
    """
    def getRequestSequence(self):
        return self.requestSequence

    """
    method to return the sequence probability
    """
    def getSequenceProb(self):
        return self.sequenceProb

    """
    method to return the sequence id = ip address
    """
    def getId(self):
        return self.sequenceId

    """
    method to set the sequence id
    """
    def setSequenceId(self,seqId):
        self.sequenceId = seqId

    """
    method to set the sequence probability
    """
    def setSequenceProb(self,seqProb):
        self.sequenceProb = seqProb

"""
class for implementing request graph
"""
class RequestGraph:
    def __init__(self):
        """
            request graph is map with key as the nodes
            and value as the 
            list[map,mycount,isChildTransProbRougliyEqually,std,mean]
        """
        self.requestGraph = {}
        self.noTransitionalProb = 0;
        self.firstPageVisitedProb = 0;
        self.totalNodesCount = 0

    """
    method to add an edge to the request graph    
    """
    def append(self,parent,child,addChildAsParent=False):
        self.totalNodesCount += 1
        if self.requestGraph.has_key(parent) == False:
            self.requestGraph[parent] = [{},1,False,0.0,0.0]
            self.requestGraph[parent][0][child] = Edge()

        else:
            self.requestGraph[parent][1] += 1
            if self.requestGraph[parent][0].has_key(child) == False:
                self.requestGraph[parent][0][child] = Edge()
            else:
                self.requestGraph[parent][0][child].incrementEdgeCount()

        #to maintain the count of all nodes, this will be called
        #only when last request in the sequences is added
        if addChildAsParent ==True:
            self.totalNodesCount += 1
            if self.requestGraph.has_key(child) == False:
                self.requestGraph[child] = [{},1,False,0.0,0.0]
            else:
                self.requestGraph[child][1] += 1
    
    """
    method to add a parent node to the request graph    
    """
    def appendNode(self,parent):
        self.totalNodesCount += 1
        if self.requestGraph.has_key(parent) == False:
            self.requestGraph[parent] = [{},1,False,0.0,0.0]
        else:
            self.requestGraph[parent][1] += 1
                
    """
        method to get the edge the transition prob
    """
    def getEdgeTransitionalProb(self,parent,child):
        try:
            return self.requestGraph[parent][0][child].getEdgeTransitionalProb()
        except KeyError:
            return self.noTransitionalProb

    """
    return Standard deviation of trans probs of childs of node
    """
    def getNodeSTD(self,node):
        if self.requestGraph.has_key(node) == True:
            return self.requestGraph[node][3]
        else:
            return self.noTransitionalProb
    """
    return mean of trans probs of childs of node
    """
    def getNodeMean(self,node):
        if self.requestGraph.has_key(node) == True:
            return self.requestGraph[node][4]
        else:
            return self.noTransitionalProb
    
    """
    set Standard deviation of trans probs of childs of node
    """
    def setNodeSTD(self,node,std):
        self.requestGraph[node][3] = std

    """
    set mean of trans probs of childs of node
    """
    def setNodeMean(self,node,mean):
        self.requestGraph[node][4] = mean

    """
    to check if the transition probabilities of child are
    rougly equal
    """
    def isChildTransProbsRoughlyEqual(self,node):
        isChidlTPREqual = False
        if self.requestGraph.has_key(node) == True:
            if (self.getNodeSTD(node)/self.getNodeMean(node))*100 < 5.0:
                isChidlTPREqual = True
        return isChidlTPREqual


    """
    method to return the probabity of node out of all the nodes visited
    """
    def getNodeVisitedProb(self,node):
        if self.requestGraph.has_key(node) == True:
            return float(self.requestGraph[node][1])/self.totalNodesCount
        else:
            return float(self.firstPageVisitedProb)
        """
        print "###################getNodeVisitedProb Start###################"
        try:
            print node,":",float(self.requestGraph[node][1])/self.totalNodesCount,\
                self.requestGraph[node][1],self.totalNodesCount
            exit(0)
            return float(self.requestGraph[node][1])/self.totalNodesCount
        except KeyError:
            print self.requestGraph.keys()
            raise            
        print "###################getNodeVisitedProb End###################"
        """

    """
    method to return the sum of edges count  from inputted parent node
    """
    def getSumOfEdgeCount(self,parent):
        sumOfEdgeCount = 0
        """
        for child in self.requestGraph[parent][0].keys():
            sumOfEdgeCount += self.requestGraph[parent][0][child].getEdgeCount()
        """
        sumOfEdgeCount += self.requestGraph[parent][1]
        return sumOfEdgeCount

    """
    method to calculate edge tranisional probabilities in the request graph   
    Note: Call it after when all edges are added to the request graph
    """
    def calculateEdgeTransitionalProb(self):
        print "\n"
        print "#############calculateEdgeTransitionalProb Started#############"
        # intilize the progress bar
        readProgBar = ProgressBar(widgets = [Bar(),Percentage()],\
            maxval=len(self.requestGraph)).start()
        status = 0
        for parent in self.requestGraph.keys():
            edgeTransProbs = []
            sumOfEdgeCount = self.getSumOfEdgeCount(parent)
            for child in self.requestGraph[parent][0].keys():
                parentNode = self.requestGraph[parent]
                edge = parentNode[0][child]
                edgeCount = edge.getEdgeCount()
                transitionalProb = float(edgeCount)/sumOfEdgeCount
                transitionalProb = float(str(round(transitionalProb,6)))
                edge.setEdgeTransitionalProb(transitionalProb)
                edgeTransProbs.append(transitionalProb)
            #calculate standard deviation and mean 
            #of edge trans probs for this parent
            self.setNodeSTD(parent,
                    float(str(round(numpy.std(edgeTransProbs),6))))
            self.setNodeMean(parent,
                    float(str(round(numpy.mean(edgeTransProbs),6))))
            #update the progress bar
            status +=1
            readProgBar.update(status)

        print "#############calculateEdgeTransitionalProb Endeedd#############"
        print "\n"


    """
    method to get sequence probability of the inputed sequence using the 
    edge transitional probabilities information from the request graph
    """
    def getSequenceProb(self,sequence):
        transitionalProbs = []
        for i in range(len(sequence)-1):
            parent = sequence[i]
            child = sequence[i+1]
            try:
                edge = self.requestGraph[parent][0][child]
                transitionalProbs.append(edge.getEdgeTransitionalProb())
            except KeyError:
                transitionalProbs.append(self.noTransitionalProb)
        """
        sequenceProb = float(self.firstPageVisitedProb+sum(transitionalProbs))\
                        /(1+len(transitionalProbs))
        """
        sequenceProb = float(self.getNodeVisitedProb(sequence[0])+\
                sum(transitionalProbs))/(1+len(transitionalProbs))

        return float(str(round(sequenceProb,6)))
    
    """
    method to get sequence probability of the inputed sequence using the 
    edge transitional probabilities information from the request graph
    and from the dir request graph
    """
    def getSequenceProbCombined1(self,sequence,dirRequestGraph,
            parentDirToFileGraph,reqMap):
        transitionalProbs = []
        dirEdgeTransitionalProbs = []
        for i in range(len(sequence)-1):
            parent = sequence[i]
            child = sequence[i+1]
            #get parent,child for dir request graph
            """
            dirParent = str(str(os.path.dirname(parent)))
            dirChild = str(str(os.path.dirname(child)))
            """
            dirParent = reqMap.getDirIntFromFileInt(parent)
            dirChild = reqMap.getDirIntFromFileInt(child)
            
            edgeTP =self.getEdgeTransitionalProb(parent,child)  
            dirEdgeTP =dirRequestGraph.getEdgeTransitionalProb(\
                    dirParent,dirChild)  
            if parentDirToFileGraph.isChildTransProbsRoughlyEqual(dirChild):
                edgeTP = dirEdgeTP
            transitionalProbs.append(edgeTP)
            dirEdgeTransitionalProbs.append(dirEdgeTP)
        """        
        combined1SequenceProb = float(self.firstPageVisitedProb+\
                sum(transitionalProbs))/\
                (1+len(dirEdgeTransitionalProbs))
        """
        #dirFirstNode = str(str(os.path.dirname(sequence[0])))
        dirFirstNode = reqMap.getDirIntFromFileInt(sequence[0])
        firstNodeVisitedProb = float(self.getNodeVisitedProb(sequence[0]))
        if parentDirToFileGraph.isChildTransProbsRoughlyEqual(dirFirstNode):
            firstNodeVisitedProb = float(dirRequestGraph.getNodeVisitedProb(
                    dirFirstNode))

        combined1SequenceProb = (firstNodeVisitedProb+sum(transitionalProbs))/\
            (1+len(dirEdgeTransitionalProbs))

        return float(str(round(combined1SequenceProb,6)))
    
    """
    method to test sequence using thresholds value
    """
    def testSequence(self,sequence,thresholds):
        testResults = {}
        for threshold in thresholds:
            testResults[threshold] = [False,len(sequence)]
            """
            curSeqProb = self.firstPageVisitedProb
            """
            curSeqProb = self.getNodeVisitedProb(sequence[0])
            curSeqLen = 1
            for i in range(len(sequence)-1):
                parent = sequence[i]
                child = sequence[i+1]
                edgeTP = None
                try:
                    edge = self.requestGraph[parent][0][child]
                    edgeTP = edge.getEdgeTransitionalProb()
                except KeyError:
                    edgeTP = self.noTransitionalProb
                curSeqLen += 1
                curSeqProb += edgeTP
                if (curSeqProb/float(curSeqLen)) < threshold:
                    #if curSeqLen is less than 3 then dont mark this as attacker 
                    if curSeqLen >=MINIMUM_TEST_SEQUENCE_LENGTH:
                        testResults[threshold] = [True,curSeqLen]
                        break

        return testResults
    
    """
    method to test the sequence using thresholds and the combined1 formula
    """
    def testSequenceCombined1(self,sequence,dirRequestGraph,parentDirToFileGraph,
            thresholds,reqMap):
        testResults = {}
        for threshold in thresholds:
            testResults[threshold] = [False,len(sequence)]
            """
            curSeqProb = self.firstPageVisitedProb
            """
            #dirFirstNode = str(str(os.path.dirname(sequence[0])))
            dirFirstNode = reqMap.getDirIntFromFileInt(sequence[0])
            curSeqProb = self.getNodeVisitedProb(sequence[0])
            if parentDirToFileGraph.isChildTransProbsRoughlyEqual(dirFirstNode):
                curSeqProb = dirRequestGraph.getNodeVisitedProb(dirFirstNode)
            curSeqLen = 1
            for i in range(len(sequence)-1):
                parent = sequence[i]
                child = sequence[i+1]
                #get parent,child for dir request graph
                """
                dirParent = str(str(os.path.dirname(parent)))
                dirChild = str(str(os.path.dirname(child)))
                """
                dirParent = reqMap.getDirIntFromFileInt(parent)
                dirChild = reqMap.getDirIntFromFileInt(child)

                fileEdgeTP =self.getEdgeTransitionalProb(parent,child)  
                dirEdgeTP =dirRequestGraph.getEdgeTransitionalProb(\
                        dirParent,dirChild)  
                 
                edgeTP = fileEdgeTP
                if parentDirToFileGraph.isChildTransProbsRoughlyEqual(dirChild):
                    edgeTP = dirEdgeTP

                curSeqProb += edgeTP
                curSeqLen += 1
                if (curSeqProb/float(curSeqLen)) < threshold:
                    #if curSeqLen is less than 3 then dont mark this as attacker 
                    if curSeqLen >=MINIMUM_TEST_SEQUENCE_LENGTH:
                        testResults[threshold] = [True,curSeqLen]
                        break
        return testResults
    """
    method to custom show the request graph
    """
    def cshow(self):
        print "##################cshow starts###################"
        for parent in self.requestGraph.keys():
            print parent
        print "\n"
        print "##################cshow Ends###################"

    """
    method to show the request graph
    """
    def show(self):
        for parent in self.requestGraph.keys():
            print "ParentFreq",self.getNodeVisitedProb(parent),\
                self.totalNodesCount,self.requestGraph[parent][1]
            for child in self.requestGraph[parent][0].keys():
                parentNode = self.requestGraph[parent]
                edge = parentNode[0][child]
                edgeCount = edge.getEdgeCount()
                tProb = edge.getEdgeTransitionalProb()
                print "['"+str(parent)+"'->'"+str(child)+\
                        "']="+str(edgeCount)+","+str(tProb)
    """
    method to get the attacker sequence, generated
    using the nodes in the request graph
    """
    def getAttackerSequences(self,numberOfAttackers):
        print "\n"
        print "#############getAttackerSequences Started###############"
        """
        numberOfSequecefactor will affect the number of sequences
        that we will be generated
        """
        numberOfSequenceFactor = 8
        #intilized the ip address of the first attacker
        currentAttackerIp = FIRST_ATTACKER_IP
        prevAttackerIp = None
        random.seed()
        attackerSequences = []
        #get the list of nodes equally weighted
        equallyWeightedNodeList = [key for key in self.requestGraph]
        #get the number of attacker sequences to generate
        """
        numberOfAttackerSequences = (len(equallyWeightedNodeList) <<\
                                     numberOfSequenceFactor\
                                    )
        """
        #Note: due to a bug in xls sheet library we can
        #have maximum 65535 sequences, but for safety we 
        #will return only return 65000 sequences
        numberOfAttackerSequences = numberOfAttackers
        if numberOfAttackerSequences > 65000:
            numberOfAttackerSequences = 65000
        
        # intilize the progress bar
        readProgBar = ProgressBar(widgets = [Bar(),Percentage()],\
            maxval=numberOfAttackerSequences).start()

        for i in range(numberOfAttackerSequences):
            #now get the list of random Sequnce objects with random seq len
            randomSequenceLength = random.randint(MIN_ATTACKER_SEQUENCE_LENGTH,
                    MAX_ATTACKER_SEQUENCE_LENGTH)
            #sequence id
            seqId = None
            if prevAttackerIp is None:
                seqId = FIRST_ATTACKER_IP                
            else:
                seqId = incrementIp(prevAttackerIp)
            #create a empty sequence object
            attackerSeq = Sequence(seqId)
            #set prevAttackerIp
            prevAttackerIp = seqId
            for j in range(randomSequenceLength):
                #now append random selected request
                attackerSeq.append(random.choice(equallyWeightedNodeList))
            #append the seq to the attackerSequences
            attackerSequences.append(attackerSeq)
            
            #update the progress bar
            readProgBar.update(i+1)
        
        print "#############getAttackerSequences Ended###############"
        print "\n"
        return attackerSequences

    """
    method to write the request Graph to the file
    """

    """
    if type = 0 use file mapping
       type =1 use dir mapping
    """
    def writeToFile(self,fileName,reqMap,graphType=0):
        space = " "
        colWidth = 48
        colWidth2 = 16
        try:
            requestGraphOutStream = open(fileName,"w")
        except:
            print "Error Opening request graph output file: ",fileName

        #first write header    
        header = "ParentNode"+colWidth*space+\
                    "ParentFreq"+colWidth2*space+\
                    "ChildNode"+colWidth*space+\
                    "EdgeCount"+colWidth2*space+\
                    "EdgeTransitionalProb\n"
        requestGraphOutStream.write(header)
        for parentInt in self.requestGraph.keys():
            parent = reqMap.getFileStr(parentInt)
            if graphType == 1:
                parent = reqMap.getDirStr(parentInt)

            parentFreq = str(self.getNodeVisitedProb(parent))
            parentOutString = str(parent)+\
                              ((len("ParentNode")-len(parent)+colWidth)*space)+\
                                str(parentFreq)+"\n"
            requestGraphOutStream.write(parentOutString)
            startPosition =(
                    (len(parent))*space+\
                    (len("ParentNode")-len(parent)+colWidth)*space+\
                    (len(parentFreq))*space+\
                    (len("ParentFreq")-len(parentFreq)+colWidth2)*space
                    )
#                    (len("ParentFreq")-len(parentFreq)+colWidth2))*space)
            for childInt in self.requestGraph[parentInt][0].keys():
                child = reqMap.getFileStr(childInt)
                if graphType == 1:
                    child = reqMap.getDirStr(childInt)

                edge = self.requestGraph[parentInt][0][childInt]
                edgeCount = str(edge.getEdgeCount())
                edgeTransitionalProb = str(edge.getEdgeTransitionalProb())

                edgeOutString = startPosition+\
                        str(child)+\
                        ((len("ChildNode")-len(str(child)))+colWidth)*space+\
                        edgeCount+\
                        ((len("EdgeCount")-len(edgeCount))+colWidth2)*space+\
                        edgeTransitionalProb+"\n"
                
                requestGraphOutStream.write(edgeOutString)
            #leave two lines after one parent data
            requestGraphOutStream.write("\n\n")
    """
    method to write stadard deviation of probs of chid to the file
    """
    def writeSTDToFile(self,fileName,reqMap,graphType=0):
        space = " "
        colWidth = 48
        colWidth2 = 16
        try:
            requestGraphOutStream = open(fileName,"w")
        except:
            print "Error Opening request graph output file: ",fileName

        #first write header    
        header = "ParentNode"+colWidth*space+\
                    "ParentSTD"+colWidth2*space+\
                    "ParentMean"+colWidth2*space+\
                    "isChildTPREqual"+colWidth2*space+"\n"
        requestGraphOutStream.write(header)
        for parentInt in self.requestGraph.keys():
            parent = reqMap.getFileStr(parentInt)
            if graphType == 1:
                parent = reqMap.getDirStr(parentInt)
            parentSTD = str(self.getNodeSTD(parent))
            parentMean = str(self.getNodeMean(parent))
            isChildTPREqual = str(self.isChildTransProbsRoughlyEqual(parent))
            
            parentOutString = str(parent)+\
                              ((len("ParentNode")-len(parent)+colWidth)*space)+\
                                str(parentSTD)+\
                              ((len("ParentSTD")-len(parentSTD)+colWidth2)*space)+\
                                str(parentMean)+\
                              ((len("ParentMean")-len(parentMean)+colWidth2)*space)+\
                                str(isChildTPREqual)+"\n"
            requestGraphOutStream.write(parentOutString)

"""
funtion which takes ip and returns incremented ip
"""
def incrementIp(ip):
    splittedIp = ip.split(".")
    
    if int(splittedIp[3]) < 255:
        splittedIp[3] = str(int(splittedIp[3])+1)
    elif int(splittedIp[2]) < 255:
        splittedIp[2] = str(int(splittedIp[2])+1)
        splittedIp[3] = str(int(0))
    elif int(splittedIp[1]) < 255:
        splittedIp[1] = str(int(splittedIp[1])+1)
        splittedIp[2] = str(int(0))
        splittedIp[3] = str(int(0))
    elif int(splittedIp[0]) < 223 and int(splittedIp[0]) >= 192:
        splittedIp[0] = str(int(splittedIp[0])+1)
        splittedIp[1] = str(int(0))
        splittedIp[2] = str(int(0))
        splittedIp[3] = str(int(0))
    else:
        raise ValueError('ip range overflowed')
    #return the new ip string
    return ".".join([octet for octet in splittedIp])
        
        

"""
Edge class for keeping details
regarding edge frequency(or count) , edge transitional probability
"""
class Edge():
    def __init__(self):
        self.edgeCount = 1
        self.edgeTransitionalProb = 0

    def getEdgeTransitionalProb(self):
        return self.edgeTransitionalProb

    def setEdgeTransitionalProb(self,transProb):
        self.edgeTransitionalProb = transProb

    def incrementEdgeCount(self):
        self.edgeCount += 1

    def getEdgeCount(self):
        return self.edgeCount

"""
get Attacker Sequences using requests from mapping file
seqType = 0 for fileSequence
          1 for dirSequence
"""
def getAttackerSequences(numberOfAttackers,reqMap,seqType=0):
    numberOfAttackers = 100000
    print "\n"
    print "#############getAttackerSequences using ReqMap Started############"
    print "TotalNumberOfAttackers: ",numberOfAttackers
    #intilized the ip address of the first attacker
    currentAttackerIp = FIRST_ATTACKER_IP
    prevAttackerIp = None
    random.seed()
    attackerSequences = []
    #get the list of nodes equally weighted
    equallyWeightedNodeList = reqMap.getAllFileInt()
    if seqType == 1:
        equallyWeightedNodeList = reqMap.getAllDirInt()

    #get the number of attacker sequences to generate

    #Note: due to a bug in xls sheet library we can
    #have maximum 65535 sequences, but for safety we 
    #will return only return 65000 sequences
    numberOfAttackerSequences = numberOfAttackers
    """
    if numberOfAttackerSequences > 65000:
        numberOfAttackerSequences = 65000
    """      
    # intilize the progress bar
    readProgBar = ProgressBar(widgets = [Bar(),Percentage()],\
        maxval=numberOfAttackerSequences).start()

    for i in range(numberOfAttackerSequences):
        #now get the list of random Sequnce objects with random seq len
        randomSequenceLength = random.randint(MIN_ATTACKER_SEQUENCE_LENGTH,
                MAX_ATTACKER_SEQUENCE_LENGTH)

        #randomSequenceLength = 1000

        #sequence id
        seqId = None
        if prevAttackerIp is None:
            seqId = FIRST_ATTACKER_IP                
        else:
            seqId = incrementIp(prevAttackerIp)

        #create a empty sequence object
        attackerSeq = Sequence(seqId)
        #set prevAttackerIp
        prevAttackerIp = seqId
        for j in range(randomSequenceLength):
            #now append random selected request
            attackerSeq.append(random.choice(equallyWeightedNodeList))
        #append the seq to the attackerSequences
        attackerSequences.append(attackerSeq)
            
        #update the progress bar
        readProgBar.update(i+1)
        
    print "#############getAttackerSequences using reqMap Ended##############"
    print "\n"
    return attackerSequences

