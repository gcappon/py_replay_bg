import numpy as np
from replay_bg import replay_bg

modality = 'identification'
data = np.array([1,2,3])
BW = 100
scenario = 'single-meal'
save_name = 'test'

replay_bg(modality = modality, data = data, BW = BW, scenario = scenario, save_name = save_name)
