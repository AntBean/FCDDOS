import os,sys
from RequestSemanticModel import RequestGraph, Edge, Sequence
from RequestSemanticModel import showSequencesProb
from RequestSemanticModel import writeSequencesProbToFile


rg = RequestGraph()

sequence1 = ['a','b','c','a','b','c','a','b','c']
sequence2 = ['a','b','d']
sequence3 = ['a','c','e']
sequence4 = ['a','c','f']
sequence5 = ['a','c']

testSeq1 = ['a','b','c','a','b','c','a','b','d']
testSeq2 = ['a','b','c','e']
testSeq3 = ['c','a','c','f']

testSeqs = [testSeq1, testSeq2, testSeq3]


sequences = [sequence1, sequence2, sequence3,sequence4, sequence5]

for sequence in sequences:
    parent = None
    child = None
    for node in sequence:
        if parent is None:
            parent = node
            continue
        else:
            child = node
            rg.append(parent,child)
            parent = child

rg.show()
rg.calculateEdgeTransitionalProb()
print "EdgeTransitionalProb"
rg.show()

#create sequence objets
seqs = []
seqId = 0
for testSeq in testSeqs:
    seq = Sequence(seqId)
    seqId +=1
    for req in testSeq:
        seq.append(req)
    seqs.append(seq)

print "sequence Probabilites"
for seq in seqs:
    seq.calculateSequenceProb(rg)
    #print seq.getId(),"=",seq.getSequenceProb(),","
showSequencesProb(seqs)

writeSequencesProbToFile(seqs,"SequenceProbTemp")

