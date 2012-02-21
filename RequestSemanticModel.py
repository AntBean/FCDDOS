import os,sys

"""
method to show the sequence probabilites for all the sequences
"""
def showSequencesProb(sequences):
    for index in range(len(sequences)):
        sequenceId = sequences[index].getId()
        sequenceProb = sequences[index].getSequenceProb()
        print "["+str(sequenceId)+"]="+str(sequenceProb)

class Sequence:
    def __init__(self,seqId):
        self.requestSequence = []
        self.sequenceId = seqId
        self.sequenceProb = 0

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
    method to return the sum of edges count  from inputted parent node
    """
    def getSumOfEdgeCount(self,parent):
        sum = 0
        for child in self.requestGraph[parent].keys():
            sum += self.requestGraph[parent][child].getEdgeCount()
        return sum
        
    """
    method to calculate edge tranisional probabilities in the request graph   
    Note: Call it after when all edges are added to the request graph
    """
    def calculateEdgeTransitionalProb(self):
        for parent in self.requestGraph.keys():
            for child in self.requestGraph[parent].keys():
                parentNode = self.requestGraph[parent]
                edge = parentNode[child]
                edgeCount = edge.getEdgeCount()
                sumOfEdgeCount = self.getSumOfEdgeCount(parent)
                transitionalProb = float(edgeCount)/sumOfEdgeCount
                transitionalProb = float(str(round(transitionalProb,2)))
                edge.setEdgeTransitionalProb(transitionalProb)


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

