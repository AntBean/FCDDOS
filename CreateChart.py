import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from collections import deque
import sys
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
        plt.semilogx()
    
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
    #plt.legend( tuple(line_list),tuple(confname_list),bbox_to_anchor=(0., 1.02, 1., .102), ncol=2,loc=3,mode="expand", borderaxespad=0.)
    #plt.legend( tuple(line_list),tuple(confname_list), prop =fp, loc=3, bbox_to_anchor=(-0.2,0),borderaxespad=0.)
    #plt.xticks((np.arange(0,max_x+10-(max_x%10)+2*((max_x+10-(max_x%10))/max_xn),(max_x+10-(max_x%10))/max_xn)))
    #plt.yticks((np.arange(0,max_y+10-(max_y%10)+2*((max_y+10-(max_y%10))/max_yn),(max_y+10-(max_y%10))/max_yn)))
    plt.savefig(chartName, format='png') 
    plt.close()
    return True







#usage of CreateChart function
xAxisData1 = [1,1,1,2,2,2,3,3,4,5]
yAxisData1 = [0.9,0.8,0.7,0.6,0.5,0.4,0.3,0.2,0.1,0.05]
xAxisData2 = [4,4,4,5,5,5,5,5,6,6]
yAxisData2 = [0.9,0.8,0.7,0.6,0.5,0.4,0.3,0.2,0.1,0.05]
userData=["ISI1te",xAxisData1,yAxisData1]
attackerData=["ISI1te",xAxisData2,yAxisData2]
chartData = [userData,attackerData]

CreateDotChart("ISI1",chartData,"SeqLen","SeqProb","SeqProv Vs SeqLen")
