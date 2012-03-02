import os, sys, random
from progressbar import ProgressBar , Percentage, Bar

#global variables
MAX_ATTACKER_SEQUENCE_LENGTH = 1000
MIN_ATTACKER_SEQUENCE_LENGTH = 2
FIRST_ATTACKER_IP = "194.0.0.1"

"""
method to write sequeces probabilities to the text file
"""
def writeSequencesProbToFile(sequences, fileName):
    space = " "
    colWidth = 16
    try:
        seqProbOutStream = open(fileName,"w")
    except:
        print "Error Opening sequence prob output file: ",fileName

    #first write header    
    header = "SequenceId"+colWidth*space+"SequenceProb"+\
            +colWidth*space+"SequenceLength"\
            +colWidth*space+"RequestSequence\n"
    seqProbOutStream.write(header)

    for sequence in sequences:
        sequenceId = str(sequence.getId())
        sequenceProb = str(sequence.getSequenceProb())
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
        for request in sequence.getRequestSequence():
            requestOutString = startPosition+str(request)+"\n"
            seqProbOutStream.write(requestOutString)

"""
method to write attackersequeces probabilities to the text file
"""
def writeAttackerSequencesProbToFile(sequences, fileName):
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
        for request in sequence.getRequestSequence():
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

class Sequence:
    def __init__(self,seqId):
        self.requestSequence = []
        self.sequenceId = seqId
        self.sequenceProb = 0

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
    def calculateSequenceProb(self,requestGraph):
        requestSequence = self.getRequestSequence()
        self.setSequenceProb(requestGraph.getSequenceProb(\
                                                          requestSequence))
    """
    method to calculate combined1 sequences probability using file level as 
        well as directory level information
        sequences must contain file level information
    """
    def calculateSequenceProbCombined1(self,dirRequestGraph,fileRequestGraph):
        requestSequence = self.getRequestSequence()
        self.setSequenceProb(fileRequestGraph.getSequenceProbCombined1(\
                    requestSequence,dirRequestGraph))

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
        self.requestGraph = {}
        self.noTransitionalProb = 0;
        self.firstPageVisitedProb = 1;

    """
    method to add an edge to the request graph    
    """
    def append(self,parent,child):
        if self.requestGraph.has_key(parent) == False:
            self.requestGraph[parent] = {}
            self.requestGraph[parent][child] = Edge()

        else:
            if self.requestGraph[parent].has_key(child) == False:
                self.requestGraph[parent][child] = Edge()
            else:
                self.requestGraph[parent][child].incrementEdgeCount()
    """
        method to get the edge the transition prob
    """
    def getEdgeTransitionalProb(self,parent,child):
        try:
            return self.requestGraph[parent][child].getEdgeTransitionalProb()
        except KeyError:
            return self.noTransitionalProb


    """
    method to return the sum of edges count  from inputted parent node
    """
    def getSumOfEdgeCount(self,parent):
        sumOfEdgeCount = 0
        for child in self.requestGraph[parent].keys():
            sumOfEdgeCount += self.requestGraph[parent][child].getEdgeCount()
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
            for child in self.requestGraph[parent].keys():
                parentNode = self.requestGraph[parent]
                edge = parentNode[child]
                edgeCount = edge.getEdgeCount()
                sumOfEdgeCount = self.getSumOfEdgeCount(parent)
                transitionalProb = float(edgeCount)/sumOfEdgeCount
                transitionalProb = float(str(round(transitionalProb,2)))
                edge.setEdgeTransitionalProb(transitionalProb)
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
                edge = self.requestGraph[parent][child]
                transitionalProbs.append(edge.getEdgeTransitionalProb())
            except KeyError:
                transitionalProbs.append(self.noTransitionalProb)
        sequenceProb = float(self.firstPageVisitedProb+sum(transitionalProbs))\
                        /(1+len(transitionalProbs))

        return float(str(round(sequenceProb,2)))
    
    """
    method to get sequence probability of the inputed sequence using the 
    edge transitional probabilities information from the request graph
    and from the dir request graph
    """
    def getSequenceProbCombined1(self,sequence,dirRequestGraph):
        transitionalProbs = []
        dirEdgeTransitionalProbs = []
        for i in range(len(sequence)-1):
            parent = sequence[i]
            child = sequence[i+1]
            #get parent,child for dir request graph
            dirParent = str(str(os.path.dirname(parent)))
            dirChild = str(str(os.path.dirname(child)))
            
            edgeTP =self.getEdgeTransitionalProb(parent,child)  
            dirEdgeTP =dirRequestGraph.getEdgeTransitionalProb(\
                    dirParent,dirChild)  

            transitionalProbs.append(edgeTP*dirEdgeTP)
            dirEdgeTransitionalProbs.append(dirEdgeTP)
                
        combined1SequenceProb = float(self.firstPageVisitedProb+\
                sum(transitionalProbs))/\
                (1+len(dirEdgeTransitionalProbs))

        return float(str(round(combined1SequenceProb,2)))

    """
    method to show the request graph
    """
    def show(self):
        for parent in self.requestGraph.keys():
            for child in self.requestGraph[parent].keys():
                parentNode = self.requestGraph[parent]
                edge = parentNode[child]
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
    def writeToFile(self,fileName):
        space = " "
        colWidth = 64
        colWidth2 = 16
        try:
            requestGraphOutStream = open(fileName,"w")
        except:
            print "Error Opening request graph output file: ",fileName

        #first write header    
        header = "ParentNode"+colWidth*space+"ChildNode"+\
                +colWidth*space+"EdgeCount"\
                +colWidth2*space+"EdgeTransitionalProb\n"
        requestGraphOutStream.write(header)

        for parent in self.requestGraph.keys():
            parentOutString = str(parent)+"\n"
            requestGraphOutStream.write(parentOutString)
            startPosition = ((len("ParentNode")+colWidth)*space)
            for child in self.requestGraph[parent].keys():
                edge = self.requestGraph[parent][child]
                edgeCount = str(edge.getEdgeCount())
                edgeTransitionalProb = str(edge.getEdgeTransitionalProb())

                edgeOutString = startPosition+str(child)+\
                        ((len("ChildNode")-len(str(child)))+colWidth)*space+\
                        edgeCount+\
                        ((len("EdgeCount")-len(edgeCount))+colWidth2)*space+\
                        edgeTransitionalProb+"\n"
                
                requestGraphOutStream.write(edgeOutString)
            #leave two lines after one parent data
            requestGraphOutStream.write("\n\n")


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

