import numpy as np
import pandas as pd
from pandas import DataFrame
import matplotlib.pyplot as plt
import matplotlib as mlt
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
import matplotlib.dates as mdates
import datetime
from datetime import date

import os
#read & clean
data = pd.read_excel('RawData/元宝血糖记录.xlsx', index_col=None).iloc[:,0:5]
data_note = pd.read_excel('RawData/元宝血糖记录.xlsx', index_col=None).iloc[:,5].fillna(0)
date = data.iloc[:,0].fillna(0) # date
data.iloc[:,2] = data.iloc[:,2].fillna(0) #food
#define y
data_glu = data.iloc[:,3]
data_ins = data.iloc[:,4]
##process food column y
data_food_ql = data['饮食 种类-数量 / g'].apply(lambda x:''.join(filter(lambda x:ord(x)>=256 , x)) if x != 0 else 0)
data_food_qt= data['饮食 种类-数量 / g'].apply(lambda x:int(''.join(filter(str.isdigit, x))) if x != 0 else 0)
data.drop('饮食 种类-数量 / g',1,inplace = True)
data.insert(2,'food_ql',data_food_ql)
data.insert(3,'food_qt',data_food_qt)
#define x
x = range(len(data))
##glu x
date_cph = data.iloc[:,0].fillna(method='ffill')
x_time = DataFrame(np.zeros((len(data), 1)))
for i in range(0,len(data)):
    x_time.iloc[i,0]=datetime.datetime.strptime(str(date_cph.iloc[i])+str(data.iloc[i,1]), "%d-%m-%Y%H:%M:%S")
data_glu_x = [x_time.iloc[i] for i in data_glu.fillna(0)[(data_glu.fillna(0) != 0)].index ]
x_time_tick = [x_time.iloc[i] for i in range(0,len(x_time)) ]
x_time_labels = [str(data.iloc[i,1]) if data_glu.fillna(0)[i] != 0 else ' '  for i in range(0,len(data))]
#ins x
data_ins_x = [x_time.iloc[i] for i in data_ins.fillna(0)[(data_ins.fillna(0) != 0)].index ]
#food x
data_food_x = [x_time.iloc[i] for i in data_food_qt.fillna(0)[(data_food_qt.fillna(0) != 0)].index ]

#hide third  axis func
def MakeInv(ax):
    ax.set_frame_on(True)
    ax.patch.set_visible(False)
    for sp in ax.spines.values():
        sp.set_visible(False)
#date ticker
year = date[(date != 0)].reset_index(drop=True)
year_x =[x_time_tick[i]   for i in  date[(date != 0)].index]
#note ticker
note = data_note[(data_note != 0)].reset_index(drop=True)
note_x = [x_time_tick[i]   for i in  data_note[(data_note != 0)].index]
#safe valve
safe_valve = 13.88
#config figure
plt.rcParams['font.sans-serif'] = ['SimHei']
fig, host = plt.subplots(figsize=(16,9))
fig.subplots_adjust(right=0.75)
plt.style.use('bmh')
color_glu = "#2d53a2"
color_ins = '#f54d1e'
color_food = '#4a7d55'
par1 = host.twinx()
par2 = host.twinx()
par2.spines["right"].set_position(("axes", 1.1))
MakeInv(par2)
par2.spines["right"].set_visible(True)
#plot three variables
host.plot(x_time_tick,data_glu.fillna(0),c='r',alpha=0) #base line
p1, =host.plot(data_glu_x,data_glu.dropna(), color_glu, label="BloodGlucose mmol/L")
host.scatter(data_glu_x,data_glu.dropna(),c='b',marker='o')
p2 = par1.scatter(data_ins_x, data_ins.dropna(), c=color_ins,label="Insulin μL")
p3 = par2.scatter(data_food_x, data_food_qt[(data_food_qt != 0)], c=color_food, label="Food gramm")
#host.set_xlim(0,x_time.iloc[-1,0] )
host.set_ylim(0, 1.1*max(data_glu))
par1.set_ylim(0, 1.7*max(data_ins.fillna(0)))
par2.set_ylim(1, 60)
par1.grid(False)
par2.grid(False)
#set label
host.set_xlabel("Time")
host.set_ylabel("BloodGlucose(mmol/L)",fontsize=18)
par1.set_ylabel("Insulin(μL)",fontsize=18)
par2.set_ylabel("Food(g)",fontsize=18)
host.yaxis.label.set_color(color_glu)
par1.yaxis.label.set_color(color_ins)
par2.yaxis.label.set_color(color_food)
tkw = dict(size=4, width=1.5)
host.tick_params(axis='y', colors=color_glu, **tkw)
par1.tick_params(axis='y', colors=color_ins, **tkw)
par2.tick_params(axis='y', colors=color_food, **tkw)
host.tick_params(axis='x', **tkw)
#set ticker
#if len(data)>60:
plt.gca().set_xticklabels(x_time_labels)
plt.xticks(x_time_tick)
host.tick_params(axis='x', rotation=60,labelsize =8)

##date ticker
for i in range(0,len(year)):
    plt.text(year_x[i], 1.5, year[i],rotation=45,horizontalalignment='left')
##note ticker
for i in range(0,len(note)):
    plt.text(note_x[i], 2, note[i],rotation=45,horizontalalignment='center',fontsize=8)
#set legend
lines = [p1, p2, p3]
legend = host.legend(lines, [l.get_label() for l in lines],facecolor='w')
plt.title("Yuanbao BG & Insulin Monitor Plot",fontsize=22)
#plot safe valve
host.plot(x_time_tick, data_glu.fillna(0)*0+safe_valve, linestyle=':',color='y')
host.text(x_time_tick[0], 14.3, 'Safe Valve 13.88',horizontalalignment='right')
plt.show()
#update file
plt.savefig("plot/yuanbao_"+str(datetime.datetime.now().strftime("%H%M_%d%m%Y")))
