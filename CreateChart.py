import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from collections import deque
import sys
from array import array
import pylab
"""
method to create a Dot chart
"""
def CreateDotChart(chartName,chartData,xLable,yLable,chartTitle):
    colours= deque(['g','r'])
    symbols= deque(['o','d'])
    lables = deque(['User','Attacker'])
    # change the size of chart using figsize parameter
    fig =plt.figure(figsize=(10,5))
    plt.title(chartTitle)
    max_x = None
    max_y = None
    max_xn = None
    max_yn = None
    lineList = []
    lineNameList = []

    ax = fig.add_subplot(111)
    for data in chartData:
        lineName, xAxisData,yAxisData= data;
        if len(colours) == 0:
            print >> sys.stderr, "not enough colour for seperation of line"
            return False
        color = colours.popleft()
        symbol = symbols.popleft()
        ax.scatter(xAxisData[0:], yAxisData[0:], c=color, s=20,\
                marker = symbol, label = lables.popleft())
        ax.set_xscale('log')
    #plt.semilogx()
    #plt.semilogy()
    
    #set properites for legend
    #fp =  matplotlib.font_manager.FontProperties(size='xx-small')
    #plt.legend(('User',"Attacker"), loc='best',prop=fp)
    #plt.legend(('User',"Attacker"), loc='best')
    plt.legend(loc='best')
    #ticks = arange(-0.06, 0.061, 0.02)
    #xticks(ticks)
    #yticks(ticks)

    ax.set_xlabel(xLable, fontsize=20)
    ax.set_ylabel(yLable, fontsize=20)
    ax.set_title(chartTitle)
    ax.grid(True)
    plt.savefig(chartName, format='png') 
    plt.close()
    return True


"""
method to create a Line chart
"""
def CreateLineChart(chartName,chartData,xLable,yLable,chartTitle):
    colours= deque(['g','r'])
    symbols= deque(['o','o'])
    lables = deque(['User','Attacker'])
    # change the size of chart using figsize parameter
    fig =plt.figure(figsize=(10,5))
    plt.title(chartTitle)
    max_x = None
    max_y = None
    max_xn = None
    max_yn = None
    lineList = []
    lineNameList = []

    ax = fig.add_subplot(111)
    for data in chartData:
        lineName, xAxisData,yAxisData= data;
        if len(colours) == 0:
            print >> sys.stderr, "not enough colour for seperation of line"
            return False
        fmt = colours.popleft()+'-o'
        symbol = symbols.popleft()
        plt.plot(xAxisData,yAxisData, fmt, label=lables.popleft())
        ax.set_xscale('log')
    
    #set properites for legend
    #fp =  matplotlib.font_manager.FontProperties(size='xx-small')
    #plt.legend(('User',"Attacker"), loc='best',prop=fp)
    #plt.legend(('User',"Attacker"), loc='best')
    #plt.legend(loc='best')
    #ticks = pylab.arange(0.0,1.0)
    #pylab.xticks(ticks)
    #yticks(ticks)

    ax.set_xlabel(xLable, fontsize=20)
    ax.set_ylabel(yLable, fontsize=20)
    ax.set_title(chartTitle)
    ax.grid(True)
    plt.savefig(chartName, format='png') 
    plt.close()
    return True




"""
#usage of CreateChart function
xAxisData1 = [1,1,1,2,2,2,3,3,4,5]
yAxisData1 = [0.9,0.8,0.7,0.6,0.5,0.4,0.3,0.2,0.1,0.05]
xAxisData2 = [4,4,4,5,5,5,5,5,6,6]
yAxisData2 = [0.9,0.8,0.7,0.6,0.5,0.4,0.3,0.2,0.1,0.05]
userData=["ISI1te",xAxisData1,yAxisData1]
attackerData=["ISI1te",xAxisData2,yAxisData2]
chartData = [userData,attackerData]

#cdfChartData = [userCDFData,attackerCDFData]
CreateDotChart("ISI1",chartData,"SeqLen","SeqProb","SeqProv Vs SeqLen")
CreateLineChart("ISI1",chartData,"SeqLen","SeqProb","SeqProv Vs SeqLen")
"""
