---
sidebar: heading
docsDir: 'docs/'
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


### Structure
The single-meal blueprint is composed of three main subsystems: subcutaneous insulin absorption, oral
glucose absorption, and glucose-insulin kinetics.  

#### Subcutaneous Insulin Absorption Subsystem
The subsystem of subcutaneous insulin absorption system is composed of three compartments and describes the 
absorption dynamics of exogenous insulin infusion to the plasma. Exogenous insulin $I(t)$ is infused to the 
first compartment, which represents insulin in a non-monomeric state. Then, "non-monomeric" insulin diffuses 
to the second compartment, representing insulin in a monomeric state, and eventually reaches plasma. 
Model equations are:

$
\begin{cases}
   \dot{I}_{sc1}(t) = -  k_d \cdot I_{sc1}(t)  + I(t-\beta)/V_I \\
   \dot{I}_{sc2}(t) = k_{d} \cdot I_{sc1}(t) - k_{a2} \cdot I_{sc2}(t) \\
   \dot{I}_{p}(t) = k_{a2}\cdot I_{sc2} - k_e \cdot I_p(t)
\end{cases}
$

where $I_{sc1}$ (mU/kg) and $I_{sc2}$ (mU/kg) represent the insulin in a non-monomeric and monomeric state, 
respectively; $I_p$ (mU/l) is the plasma insulin concentration;
$k_d$ (min$^{-1}$) is the rate constant of diffusion from the first to the second compartment;  $k_{a2}$ (min$^{-1}$) 
is  the rate constant of subcutaneous insulin absorption from the second compartment to the plasma; $k_e$ (min$^{-1}$) 
is the fractional clearance rate; $V_I$ (l/kg) is the volume of insulin distribution; $\beta$ (min) is the delay in 
the appearance of insulin in the first compartment.  

#### Oral Glucose Absorption Subsystem
The subsystem of oral glucose absorption system describes the gastro-intestinal tract as a three-compartment system: 
the first two compartments quantify the glucose in the stomach, while the third compartment models the upper small 
intestine where CHO is absorbed. 
Model equations are: 

$
\begin{cases}
   \dot{Q}_{sto1}(t) = - k_{empt}\cdot Q_{sto1}(t)  + CHO(t) \\
   \dot{Q}_{sto2}(t) = k_{empt}\cdot Q_{sto1}(t) - k_{empt}\cdot Q_{sto2}(t)\\
   \dot{Q}_{gut}(t) = k_{empt}\cdot Q_{sto2}(t) - k_{abs}\cdot Q_{gut}(t)
\end{cases}
$

where $Q_{sto1}$ (mg / kg) and $Q_{sto2}$ (mg / kg) are the amounts of glucose in the stomach in solid and liquid 
state, respectively; $Q_{gut}$ (mg/kg) is the glucose concentration in the intestine; $k_{empt}$ (min$^{-1}$) 
is the rate constant of gastric emptying; $k_{abs}$ (min$^{-1}$) is the rate constant of intestinal absorption; 
$CHO$ (mg/kg/min) is the ingested carbohydrate rate. Model (\ref{eq:oral}) allows to estimate the rate of glucose 
appearance in plasma $Ra$ (mg/kg/min) as:

$
Ra(t) = f\cdot k_{abs} \cdot Q_{gut}(t)
$

where $f$ (dimensionless) is the fraction of the intestinal content absorbed in the plasma.

#### Glucose-Insulin Kinetics Subsystem
The subsystem is composed of three compartments, the first describing the effect of insulin action and oral
glucose rate of appearance on plasma glucose concentration, the second quantifies the impact of plasma insulin 
concentration on insulin action, and the last one represents the transport of glucose from plasma to the interstitium. 
Model equations are:

$
\begin{cases}
   \dot{G}(t) = - [SG + \rho(G) X(t)] \cdot G(t) + SG \cdot G_b + Ra(t) / V_G \\
   \dot{X}(t) = - p_2 \cdot [X(t) - SI\cdot(I_p(t)-I_{pb})] \\
   \dot{IG}(t) = - \frac{1}{\alpha}(IG(t) - G(t))
\end{cases}
$

where $G$ (mg/dl) is the plasma glucose concentration, $X$ (min$^{-1}$) is the insulin action on glucose disposal and production; $IG$ (mg/dl) is the interstitial glucose concentration; $SG$ (min$^{-1}$) is the glucose effectiveness that describes the glucose ability to promote glucose disposal and inhibit glucose production; $G_b$ (mg/dl) is the basal glucose concentration in the plasma; $V_G$ (dl/kg) is the volume of glucose distribution; $p_2$ (min$^{-1}$) is the rate constant of insulin action dynamics; $SI$ (ml/$\mu$U$\cdot$min) is the insulin sensitivity; $I_{pb}$ (mU/l) is the basal insulin concentration in the plasma; $\alpha$ (min) is the delay between plasmatic and IG compartments; and $\rho(G)$, is a deterministic function, introduced by Dalla Man et al. \cite{dallaManNewSim}, that allows to better represent glucose dynamics in the hypoglycemic range by increasing insulin action when glucose decreases below a certain threshold:

$
\begin{align}
    \rho(G)  & =\! 
    \begin{cases}
        1 \hspace{5.04cm}\quad \text{if }  G \geq G_b \\
        1 \!+\! 10 r_1 \{ [ln(G)]^{r_2} - [ln(G_b)]^{r_2} \}^2  \\
        \hspace{4.24cm}\quad \text{if } G_{th}< G < G_b \\
        1 \!+\! 10 r_1 \{ [ln(G_{th})]^{r_2} - [ln(G_b)]^{r_2} \}^2 \quad \text{if } G \label{eq:risk} \leq G_{th}
    \end{cases}
\end{align}
$

where $G_{th}$ is the hypoglycemic threshold (set to 60 mg/dl) and $r_1$ (dimensionless) and $r_2$ (dimensionless) 
are two model parameters, without direct physiological interpretation, set to 1.44 and 0.81, respectively.

### Constraints

## Multi-meal

::: tip
Generally, the multi meal blueprint is the most common choice since usually one deals with
data that include more than 1 meal and more than 6/8 hours.
:::
