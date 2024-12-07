---
sidebar: auto
---
# Data Requirements

## Single Meal blueprint

A single meal blueprint can be referred to a specific period of time when a specific subject had 1 meal and a
corresponding insulin basal-bolus administration. 

To run step 1 of PyReplayBG (i.e., twinning) on a single meal blueprint, user must provide the corresponding data as
a `.csv` file containing (at least) the following mandatory columns:
* `t`: the timestamps when data of the corresponding row were recorded (format 
`DD-MMM-YYYY HH:mm:SS` for example `20-Dec-2013 10:35:00`). The sampling grid defined by the `t` column must be
homogeneous. 
* `glucose`: the glucose concentration (mg/dl) at `t`. Can contain NaN values.
* `cho`: the meal intake (g/min) at `t`. Can't contain NaN values. If no meals were recorded at `t` just put `0` there.
* `bolus`: the insulin bolus (U/min) administered at `t`. Can't contain NaN values. If no insulin boluses were 
administered at `t` just put `0` there.
* `basal`: the basal insulin (U/min) administered at `t`. Can't contain NaN values. If no basal insulin was 
administered at `t` just put `0` there.
* `bolus_label`: the type of `bolus`. Each `bolus` entry > 0 must have a label defined. Can be 
  * `B` if it is the bolus of a breakfast.
  * `L` if it is the bolus of a lunch.
  * `D` if it is the bolus of a dinner.
  * `C` if it is a corrective bolus.
  * `S` if it is the bolus of a snack.

::: tip
If `bolus_label` is not important for you (e.g., you do not plan to use it during replay) or if you do not need that, 
just add an empty `bolus_label` column. 
:::

::: warning
If more than 1 meals are present in the provided file, PyReplayBG will consider the first meal as "main" meal. The others
will be considered as "other" meals.
:::

::: tip
A representative data file of a single meal blueprint can be found in `example/data/single-meal_example.csv`
:::

## Multi meal blueprint

A multi meal blueprint can be referred to a specific period of time when a specific subject had more than 1 meal and a
corresponding insulin basal-bolus administration regimen. 

To run step 1 of PyReplayBG (i.e., twinning) on a multi meal blueprint, user must provide the corresponding data as
a `.csv` file containing (at least) the following mandatory columns:
* `t`: the timestamps when data of the corresponding row were recorded (format 
`DD-MMM-YYYY HH:mm:SS` for example `20-Dec-2013 10:35:00`). The sampling grid defined by the `t` column must be
homogeneous. 
* `glucose`: the glucose concentration (mg/dl) at `t`. Can contain NaN values.
* `cho`: the meal intake (g/min) at `t`. Can't contain NaN values. If no meals were recorded at `t` just put `0` there.
* `bolus`: the insulin bolus (U/min) administered at `t`. Can't contain NaN values. If no insulin boluses were 
administered at `t` just put `0` there.
* `basal`: the basal insulin (U/min) administered at `t`. Can't contain NaN values. If no basal insulin was 
administered at `t` just put `0` there.
* `cho_label`: the type of `cho`. Each `cho` entry > 0 must have a label defined. Can be 
  * `B` if it is a breakfast.
  * `L` if it is a lunch.
  * `D` if it is a dinner.
  * `H` if it is a hypotreatment.
  * `S` if it is a snack.
* `bolus_label`: the type of `bolus`. Each `bolus` entry > 0 must have a label defined. Can be 
  * `B` if it is the bolus of a breakfast.
  * `L` if it is the bolus of a lunch.
  * `D` if it is the bolus of a dinner.
  * `C` if it is a corrective bolus.
  * `S` if it is the bolus of a snack.

::: tip
If `bolus_label` is not important for you (e.g., you do not plan to use it during replay) or if you do not need that, 
just add an empty `bolus_label` column. 
:::

::: tip
A representative data file of a single meal blueprint can be found in `example/data/multi-meal_example.csv`
:::




firstly, an interval is split into single days. After that, the DT-T1D of the first day is created running the above mentioned twinning procedure by starting from steady state conditions. Then, the DT-T1D of the second day is created using the same procedure but setting the initial model conditions to the final model conditions of the first day. Finally, this process is iterated for each subsequent day of the interval. This process eliminates the need for the initial steady-state assumption for all days except the first, enabling the identification and simulation of longer, more comprehensive data intervals.

\textit{Remark}: It is important to note that, to make the twinning procedure more reliable, days having significant data gaps (i.e., more that 10\% of missing glucose readings) or without a single reported meal intake or insulin bolus, should be discarded to avoid the creation of DT-T1D not representing the actual underneath physiology. From the practical point-of-view, this means that, a given patient's dataset will result in the creation of one or multiple DT-T1D each corresponding to a specific interval comprising sequences of one or more consecutive days.