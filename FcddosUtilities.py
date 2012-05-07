import os,sys

"""
method return the botnet size for the given attacker parameter
"""
def getMinimumBotnetSize(NPraList):
    N1=float(NPraList[0])
    P1=float(NPraList[1])
    r1=float(NPraList[2])
    a1=float(NPraList[3])
    N2=float(NPraList[4])
    P2=float(NPraList[5])
    N3=float(NPraList[6])
    P3=float(NPraList[7])
    N4=float(NPraList[8])
    P4=float(NPraList[9])
    totalUserTime =((N4-1)*P4+N4*((N3-1)*P3+N3*((N2-1)*P2+N2*(
                        (N1-1)*P1+N1*((r1-1)*a1)))))
    if totalUserTime ==0:
        return "INF"
    totalNumberOfRequest = N4*N3*N2*N1*r1
    averageRequestRate = float(totalNumberOfRequest)/totalUserTime
    MB = int((1000/averageRequestRate)*(600/totalUserTime))
    return str(MB)
    """
    N=float(NPraList[0])
    P=float(NPraList[1])
    r=float(NPraList[2])
    a=float(NPraList[3])
    Pt = (P*(N-1))
    #MB = int(1000*(a+P/r)*(600/(Pt*(N-1)+N*r*a)))
    This should be the correct calculation as P*(N-1) will give the 
    sum of all the pauses between searching session, so again we don't need
    to multiply Pt with N-1
    MB = int(1000*(a+P/r)*(600/(P*(N-1)+N*r*a)))
    """

"""
method to convert all the items inside a list to their 
string representation
for float values round them up to round value if specified
"""
def convertListToStr(dataList,roundValue=None):
    if len(dataList) == 0:
        raise ValueError('empty list passed')
    for index in xrange(len(dataList)):
        typeOfData = type(dataList[index])
        if typeOfData == list:
            dataList[index] = convertListToStr(dataList[index],roundValue)
        elif ((typeOfData == float) and (roundValue)):
            dataList[index] = str(round(dataList[index],roundValue))
        else:
            dataList[index] = str(dataList[index])
    return dataList

"""
mylist = [1,[2,3.45567],[4,5.67878]]

print convertListToStr(mylist,3)
"""
