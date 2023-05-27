import numpy as np
import pandas as pd
from replay_bg import replay_bg
from datetime import datetime, timedelta

# Set fake data
t = np.arange(datetime(2023,1,1,6,0,0), datetime(2023,1,1,8,0,0), timedelta(minutes=5)).astype(datetime)
glucose = np.arange(120,120+t.size,1)
cho = np.zeros(t.size)
cho[0] = 10
bolus = np.zeros(t.size)
bolus[0] = 1
basal = np.zeros(t.size)+0.01/60
choLabel = np.repeat('',t.size)
choLabel[0] = 'B'
bolusLabel = np.repeat('',t.size)
bolusLabel[0] = 'B'
exercise = np.zeros(t.size)
d = {'t': t, 'glucose': glucose, 'cho': cho, 'choLabel' : choLabel, 'bolus' : bolus, 'bolusLabel' : bolusLabel, 'basal' : basal, 'exercise' : exercise}
data = pd.DataFrame(data=d)

#Set other parameters for identification
modality = 'identification'
BW = 100
scenario = 'single-meal'
save_name = 'test'
        
replay_bg(modality = modality, data = data, BW = BW, scenario = scenario, save_name = save_name)