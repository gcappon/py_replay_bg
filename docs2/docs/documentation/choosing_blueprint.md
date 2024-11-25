---
sidebar: auto
---

# Choosing blueprint

Choosing the right `blueprint` for the digital twin is one of the key choices 
to be made when using ReplayBG. This must be done when a `ReplayBG` object needs to 
be created.

As a matter of fact, the blueprint, which is associated to a specific mathematical
model, will practically represent the resulting digital twin and will define its 
domain of applicability as well as what are its final "capabilities".

So, what are the possibilities? And, most importantly, how to decide?

There are two possibilities: 
* `blueprint='single-meal'`: by "single meal" one can refer to a specific period 
of time when a specific subject had only 1 main meal and a corresponding insulin 
basal-bolus administration. Usually, this period of time spans maximum 6/8 hours,
starts near such main meal, and ends just before the subsequent main meal and/or after
a reasonable amount of time.
* `blueprint='multi-meal'`: by "multi meal" one can refer to a specific period 
of time when a specific subject had more than 1 main meal and a
corresponding insulin basal-bolus administration regimen. One can think to such 
period of time by thinking to a day, when multiple meals occur, or even multiple days.

As such, the driver through the choice of the right blueprint are the data to
be used to create the digital twin. Anyway, ReplayBG will not choose automatically the 
right blueprint based on the input data, so this aspect is up to the user.

In the following, details on the two blueprint structures are reported, as well as their 
key capabilities and constraints.

## Single-meal

The single meal blueprint is based on the following mathematical model: 


and can be pictured as 

Euler's identity $e^{i\pi}+1=0$ is a beautiful formula in $\mathbb{R}^2$.

### Constraints

## Multi-meal

::: tip
Generally, the multi meal blueprint is the most common choice since usually one deals with
data that include more than 1 meal and more than 6/8 hours.
:::
