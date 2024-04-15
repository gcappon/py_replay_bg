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
fig, axes = plt.subplots(4, 2,figsize=(15, 10))

# beta
sns.distplot(betaDistribution,ax = axes[0,0])
sns.distplot(betaDistribution_with_basal,ax = axes[0,0]).set(xlabel='Beta')

# Gb
sns.distplot(GbDistribution,ax = axes[0,1])
sns.distplot(GbDistribution_with_basal,ax = axes[0,1]).set(xlabel='Gb')

# ka2
sns.distplot(ka2Distribution,ax = axes[1,0])
sns.distplot(ka2Distribution_with_basal,ax = axes[1,0]).set(xlabel='ka2')

# kabs
sns.distplot(kabsDistribution,ax = axes[1,1])
sns.distplot(kabsDistribution_with_basal,ax = axes[1,1]).set(xlabel='kabs')

# kempt
sns.distplot(kemptDistribution,ax = axes[2,0])
sns.distplot(kemptDistribution_with_basal,ax = axes[2,0]).set(xlabel='kempt')

# kd
sns.distplot(kdDistribution,ax = axes[2,1])
sns.distplot(kdDistribution_with_basal,ax = axes[2,1]).set(xlabel='kd')

# SG
sns.distplot(SGDistribution,ax = axes[3,0])
sns.distplot(GbDistribution_with_basal,ax = axes[3,0]).set(xlabel='SG')

# SI
sns.distplot(SIDistribution,ax = axes[3,1])
sns.distplot(SIDistribution_with_basal,ax = axes[3,1]).set(xlabel='SI')


fig.legend(labels=['over basal','basal'])
plt.tight_layout()
plt.show()