# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 17:39:41 2024

@author: bio
"""
import os
import pandas as pd
import pickle
from matplotlib import pyplot as plt
import seaborn as sns

with open(os.path.join('results', 'draws','draws_test_single_meal' + '.pkl'), 'rb') as file:
    identification_results = pickle.load(file)
    

betaDistribution = identification_results['draws']['beta']['chain']
GbDistribution = identification_results['draws']['Gb']['chain']
ka2Distribution = identification_results['draws']['ka2']['chain']
kabsDistribution = identification_results['draws']['kabs']['chain']
kdDistribution = identification_results['draws']['kd']['chain']
kemptDistribution = identification_results['draws']['kempt']['chain']
SGDistribution = identification_results['draws']['SG']['chain']
SIDistribution = identification_results['draws']['SI']['chain']


with open(os.path.join('results', 'draws','draws_test_single_meal_with_insulin' + '.pkl'), 'rb') as file:
    identification_results_with_basal = pickle.load(file)
    
betaDistribution_with_basal = identification_results_with_basal['draws']['beta']['chain']
GbDistribution_with_basal = identification_results_with_basal['draws']['Gb']['chain']
ka2Distribution_with_basal = identification_results_with_basal['draws']['ka2']['chain']
kabsDistribution_with_basal = identification_results_with_basal['draws']['kabs']['chain']
kdDistribution_with_basal = identification_results_with_basal['draws']['kd']['chain']
kemptDistribution_with_basal = identification_results_with_basal['draws']['kempt']['chain']
SGDistribution_with_basal = identification_results_with_basal['draws']['SG']['chain']
SIDistribution_with_basal = identification_results_with_basal['draws']['SI']['chain']

# Create subplots
fig, axs = plt.subplots(4, 2, sharex = True, figsize=(12, 10))

# Plot data on each subplot with legends
sns.displot(betaDistribution, label='over_basal', ax=axs[0])
sns.displot(betaDistribution_with_basal, label='with_basal', ax=axs[0])
axs[0].legend()

sns.displot(GbDistribution, label='over_basal', ax=axs[0, 1])
sns.displot(GbDistribution_with_basal, label='with_basal', ax=axs[0, 1])
axs[0, 1].legend()

sns.displot(kabsDistribution, label='over_basal', ax=axs[1, 0])
sns.displot(kabsDistribution_with_basal, label='with_basal', ax=axs[1, 0])
axs[1, 0].legend()

sns.displot(SIDistribution, label='over_basal', ax=axs[1, 1])
sns.displot(SIDistribution_with_basal, label='with_basal', ax=axs[1, 1])
axs[1, 1].legend()


# Adjust layout
plt.tight_layout()

# Show plot
plt.show()