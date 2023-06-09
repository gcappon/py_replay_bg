import numpy as np
import pandas as pd
from replay_bg import ReplayBG
from datetime import datetime, timedelta

# Set fake data
t = np.arange(datetime(2023,1,1,6,0,0), datetime(2023,1,1,12,0,0), timedelta(minutes=5)).astype(datetime)
glucose = np.arange(360,360+t.size,1)
cho = np.zeros(t.size)
cho[0] = 10
#cho[5] = 20
bolus = np.zeros(t.size)
bolus[0] = 1
#bolus[5] = 2
basal = np.zeros(t.size)+0.01/60
choLabel = np.repeat('',t.size)
choLabel[0] = 'B'
bolusLabel = np.repeat('',t.size)
bolusLabel[0] = 'B'
exercise = np.zeros(t.size)
d = {'t': t, 'glucose': glucose, 'cho': cho, 'choLabel' : choLabel, 'bolus' : bolus, 'bolusLabel' : bolusLabel, 'basal' : basal, 'exercise' : exercise}
data = pd.DataFrame(data=d)

M = 10**2
N = 2*10
K = 10**4
keys = np.random.randint(M, size=(N,))
values = np.random.random((N,))
lookup_dict = dict(zip(np.arange(0,len(values)), values))
#Set other parameters for identification
modality = 'replay'
BW = 100
scenario = 'single-meal'
save_name = 'test'
short_dict = {x:x*5 for x in range(1,100)}  
rbg = ReplayBG(modality = modality, data = data, BW = BW, scenario = scenario, save_name = save_name)
rbg.run(data = data, BW = BW)