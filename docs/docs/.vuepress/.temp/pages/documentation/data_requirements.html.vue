<template><div><h1 id="data-requirements" tabindex="-1"><a class="header-anchor" href="#data-requirements"><span>Data Requirements</span></a></h1>
<h2 id="single-meal-blueprint" tabindex="-1"><a class="header-anchor" href="#single-meal-blueprint"><span>Single Meal blueprint</span></a></h2>
<p>A single meal blueprint can be referred to a specific period of time when a specific subject had 1 meal and a
corresponding insulin basal-bolus administration.</p>
<p>To run step 1 of PyReplayBG (i.e., twinning) on a single meal blueprint, user must provide the corresponding data as
a <code v-pre>.csv</code> file containing (at least) the following mandatory columns:</p>
<ul>
<li><code v-pre>t</code>: the timestamps when data of the corresponding row were recorded (format
<code v-pre>DD-MMM-YYYY HH:mm:SS</code> for example <code v-pre>20-Dec-2013 10:35:00</code>). The sampling grid defined by the <code v-pre>t</code> column must be
homogeneous.</li>
<li><code v-pre>glucose</code>: the glucose concentration (mg/dl) at <code v-pre>t</code>. Can contain NaN values.</li>
<li><code v-pre>cho</code>: the meal intake (g/min) at <code v-pre>t</code>. Can't contain NaN values. If no meals were recorded at <code v-pre>t</code> just put <code v-pre>0</code> there.</li>
<li><code v-pre>bolus</code>: the insulin bolus (U/min) administered at <code v-pre>t</code>. Can't contain NaN values. If no insulin boluses were
administered at <code v-pre>t</code> just put <code v-pre>0</code> there.</li>
<li><code v-pre>basal</code>: the basal insulin (U/min) administered at <code v-pre>t</code>. Can't contain NaN values. If no basal insulin was
administered at <code v-pre>t</code> just put <code v-pre>0</code> there.</li>
<li><code v-pre>bolus_label</code>: the type of <code v-pre>bolus</code>. Each <code v-pre>bolus</code> entry &gt; 0 must have a label defined. Can be
<ul>
<li><code v-pre>B</code> if it is the bolus of a breakfast.</li>
<li><code v-pre>L</code> if it is the bolus of a lunch.</li>
<li><code v-pre>D</code> if it is the bolus of a dinner.</li>
<li><code v-pre>C</code> if it is a corrective bolus.</li>
<li><code v-pre>S</code> if it is the bolus of a snack.</li>
</ul>
</li>
</ul>
<div class="hint-container tip">
<p class="hint-container-title">Tips</p>
<p>If <code v-pre>bolus_label</code> is not important for you (e.g., you do not plan to use it during replay) or if you do not need that,
just add an empty <code v-pre>bolus_label</code> column.</p>
</div>
<div class="hint-container warning">
<p class="hint-container-title">Warning</p>
<p>If more than 1 meals are present in the provided file, PyReplayBG will consider the first meal as &quot;main&quot; meal. The others
will be considered as &quot;other&quot; meals.</p>
</div>
<div class="hint-container tip">
<p class="hint-container-title">Tips</p>
<p>A representative data file of a single meal blueprint can be found in <code v-pre>example/data/single-meal_example.csv</code></p>
</div>
<h2 id="multi-meal-blueprint" tabindex="-1"><a class="header-anchor" href="#multi-meal-blueprint"><span>Multi meal blueprint</span></a></h2>
<p>A multi meal blueprint can be referred to a specific period of time when a specific subject had more than 1 meal and a
corresponding insulin basal-bolus administration regimen.</p>
<p>To run step 1 of PyReplayBG (i.e., twinning) on a multi meal blueprint, user must provide the corresponding data as
a <code v-pre>.csv</code> file containing (at least) the following mandatory columns:</p>
<ul>
<li><code v-pre>t</code>: the timestamps when data of the corresponding row were recorded (format
<code v-pre>DD-MMM-YYYY HH:mm:SS</code> for example <code v-pre>20-Dec-2013 10:35:00</code>). The sampling grid defined by the <code v-pre>t</code> column must be
homogeneous.</li>
<li><code v-pre>glucose</code>: the glucose concentration (mg/dl) at <code v-pre>t</code>. Can contain NaN values.</li>
<li><code v-pre>cho</code>: the meal intake (g/min) at <code v-pre>t</code>. Can't contain NaN values. If no meals were recorded at <code v-pre>t</code> just put <code v-pre>0</code> there.</li>
<li><code v-pre>bolus</code>: the insulin bolus (U/min) administered at <code v-pre>t</code>. Can't contain NaN values. If no insulin boluses were
administered at <code v-pre>t</code> just put <code v-pre>0</code> there.</li>
<li><code v-pre>basal</code>: the basal insulin (U/min) administered at <code v-pre>t</code>. Can't contain NaN values. If no basal insulin was
administered at <code v-pre>t</code> just put <code v-pre>0</code> there.</li>
<li><code v-pre>cho_label</code>: the type of <code v-pre>cho</code>. Each <code v-pre>cho</code> entry &gt; 0 must have a label defined. Can be
<ul>
<li><code v-pre>B</code> if it is a breakfast.</li>
<li><code v-pre>L</code> if it is a lunch.</li>
<li><code v-pre>D</code> if it is a dinner.</li>
<li><code v-pre>H</code> if it is a hypotreatment.</li>
<li><code v-pre>S</code> if it is a snack.</li>
</ul>
</li>
<li><code v-pre>bolus_label</code>: the type of <code v-pre>bolus</code>. Each <code v-pre>bolus</code> entry &gt; 0 must have a label defined. Can be
<ul>
<li><code v-pre>B</code> if it is the bolus of a breakfast.</li>
<li><code v-pre>L</code> if it is the bolus of a lunch.</li>
<li><code v-pre>D</code> if it is the bolus of a dinner.</li>
<li><code v-pre>C</code> if it is a corrective bolus.</li>
<li><code v-pre>S</code> if it is the bolus of a snack.</li>
</ul>
</li>
</ul>
<div class="hint-container tip">
<p class="hint-container-title">Tips</p>
<p>If <code v-pre>bolus_label</code> is not important for you (e.g., you do not plan to use it during replay) or if you do not need that,
just add an empty <code v-pre>bolus_label</code> column.</p>
</div>
<div class="hint-container tip">
<p class="hint-container-title">Tips</p>
<p>A representative data file of a single meal blueprint can be found in <code v-pre>example/data/multi-meal_example.csv</code></p>
</div>
<p>firstly, an interval is split into single days. After that, the DT-T1D of the first day is created running the above mentioned twinning procedure by starting from steady state conditions. Then, the DT-T1D of the second day is created using the same procedure but setting the initial model conditions to the final model conditions of the first day. Finally, this process is iterated for each subsequent day of the interval. This process eliminates the need for the initial steady-state assumption for all days except the first, enabling the identification and simulation of longer, more comprehensive data intervals.</p>
<p>\textit{Remark}: It is important to note that, to make the twinning procedure more reliable, days having significant data gaps (i.e., more that 10% of missing glucose readings) or without a single reported meal intake or insulin bolus, should be discarded to avoid the creation of DT-T1D not representing the actual underneath physiology. From the practical point-of-view, this means that, a given patient's dataset will result in the creation of one or multiple DT-T1D each corresponding to a specific interval comprising sequences of one or more consecutive days.</p>
</div></template>


