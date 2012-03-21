import os,sys

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
