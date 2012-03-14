import ghmm import *

"""
CHMM: custom HMM class
for dealing with GHMM
"""
"""
class CHMM:
    def __init__(self,sequences):
"""    

"""
sequence prob will be calculated only first 10 request
if the sequence is shorted then 10, then its prob will
be 0.00
"""
MAX_SEQ_LEN = 10
class CHMM:
    def __init__(self,SRG,ORG):
        #SRG is state request graph and 
        #ORG is observation request graph with
        #state as the parent and observation as child

        self.noTransitionalProb = 0.0;
        self.missedStateVisitedProb = 0.0;
        #initial state probability matrix
        self.pi = []
        #state transitional probability matrix
        self.A = []
        #emission probability matrix
        self.B = []
        # mapping of state from char to integer
        self.stateNameToNum = {}
        # mapping of state from integer to num
        self.stateNumToName = {}
        # mapping of observation from char to integer
        self.obsNameToNum = {}
        # mapping of observation from integer to num
        self.obsNumToName = {}
        #intilizeMappings
        initStateMappings(SRG);
        initObsMappings(ORG);
        #intilize matrix
        initPi(SRG)
        initA(SRG)
        initB(ORG)
        #observation domain
        sigma = IntegerRange(0,len(ORG.keys())) 
        #now create hmm the instance
        model = HMMFromMatrices(sigma, DiscreteDistribution(sigma),\
                self.A, self.B, self.pi)

    """
    method to intilize mappings
    """
    def initStateMappings(self,SRG):
        stateId = 0
        for state in SRG.requestGraph.keys():
            self.stateNameToNum[state] = stateId
            self.stateNumToName[stateId] = state
            stateId += 1
    
    def initObsMappings(self,ORG):
        obsId = 0
        for state in ORG.requestGraph.keys():
            for obs in state[0]:
                if obsNameToNum.has_key(obs) == False:
                    self.obsNameToNum[obs] = obsId
                    self.obsNumToName[obsId] = obs
                    obsId += 1
    """
    method to intilize the intial state prob matix
    """
    def initPi(self,SRG):
        for index in len(SRG.requestGraph.keys()):
            state = self.stateNumToName[index]
            self.pi[index] = float(SRG.requestGraph.getNodeVisitedProb(state))

    """
       method to initilize the transional prob matix
    """
    def initA(self,SRG):
        for row in len(SRG.requestGraph.keys()):
            parent = self.stateNumToName[row]
            parentTransProbs = []
            for col in len(SRG.requestGraph.keys()):
                child = self.stateNumToName[col]
                stateTransProb = SRG.getEdgeTransitionalProb(parent,child)
                parentTransProbs.append(float(stateTransProb)) 
            self.A.append(parentTransProbs)
    
    """
       method to initilize the emission prob matrix
    """
    def initB(self,ORG):
        for row in len(ORG.requestGraph.keys()):
            parent = self.obsNumToName[row]
            emissionProbs = []
            for col in len(ORG.requestGraph.keys()):
                child = self.obsNumToName[col]
                emissionProb = ORG.getEdgeTransitionalProb(parent,child)
                emissionProbs.append(float(emissionProb)) 
            self.B.append(emissionProbs)
    """
       method to get the sequence prob
    """
    def getSequenceProb(self,sequence):
        obsSequence = []
        for i in range(len(sequence)-1):
            if i == MAX_SEQ_LEN:
                break
            obs = self.obsNameToNum[sequence[i]]
            obsSequence.append(obs)
        if len(obsSequence) < MAX_SEQ_LEN:
            return 0.000000
        sequenceProb = model.loglikelihood(obsSequences)
        return float(str(round(sequenceProb,6)))



    """
    """
    #method to get transional prob from parent to child
    """
    def getStateTransProb(self,parent,child):
        try:
            return self.A[self.NameToNum[parent]][self.NameToNum[child]]
        except:
            return self.noTransitionalProb
    
    """
    #method to return the probabity of the state
    """
    def getStateVisitedProb(self,state):
        try:
            return self.pie[self.NameToNum[state]]
        except:
            return self.missedStateVisitedProb
 
    
    """
    #method to get sequence probability of the inputed sequence
    """
    def getSequenceProb(self,sequence):
        firstState = sequence[0]
        sequenceProb = self.getStateVisitedProb(self.NameToNum[firstState])
        for i in range(len(sequence)-1):
            parent = sequence[i]
            child = sequence[i+1]
            edgeTP = self.getStateTransProb(parent,child)
            sequenceProb *= edgeTP
        return float(str(round(sequenceProb,6)))

    """
