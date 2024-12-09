<template><div><h1 id="analyzing-replay-results" tabindex="-1"><a class="header-anchor" href="#analyzing-replay-results"><span>Analyzing replay results</span></a></h1>
<p>ReplayBG provides the possibility, to analyze in a painless way the results of <code v-pre>rbg.replay()</code>. To this aim,
ReplayBG integrates the <a href="https://github.com/gcappon/py_agata" target="_blank" rel="noopener noreferrer">AGATA</a> software for analyzing the simulated glucose and
CGM profiles, a dedicated routines for the meal/insulin events.</p>
<p>This is done using the <code v-pre>Analyzer</code> class importable from <code v-pre>py_replay_bg.analyzer</code>.</p>
<p>In the following, we show how to do that in the case of single portions of data and portions of data spanning
more than one day (i.e., intervals).</p>
<h2 id="analyzing-replay-results-from-single-portions-of-data" tabindex="-1"><a class="header-anchor" href="#analyzing-replay-results-from-single-portions-of-data"><span>Analyzing replay results from single portions of data</span></a></h2>
<p>To analyze replay results from single portions of data use the <code v-pre>Analyzer.analyze_replay_results()</code> static
method, which is formerly defined as:</p>
<div class="language-python line-numbers-mode" data-highlighter="prismjs" data-ext="py" data-title="py"><pre v-pre><code><span class="line">    <span class="token decorator annotation punctuation">@staticmethod</span></span>
<span class="line">    <span class="token keyword">def</span> <span class="token function">analyze_replay_results</span><span class="token punctuation">(</span></span>
<span class="line">            replay_results<span class="token punctuation">:</span> Dict<span class="token punctuation">,</span></span>
<span class="line">            data<span class="token punctuation">:</span> pd<span class="token punctuation">.</span>DataFrame <span class="token operator">=</span> <span class="token boolean">None</span><span class="token punctuation">,</span></span>
<span class="line">    <span class="token punctuation">)</span> <span class="token operator">-</span><span class="token operator">></span> Dict</span>
<span class="line"></span></code></pre>
<div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h3 id="input-parameters" tabindex="-1"><a class="header-anchor" href="#input-parameters"><span>Input parameters</span></a></h3>
<ul>
<li><code v-pre>replay_results</code>: the dictionary returned by or saved with the <code v-pre>rbg.replay()</code> method</li>
<li><code v-pre>data</code>, optional, default: <code v-pre>None</code>: The <code v-pre>data</code> parameter passed to <code v-pre>rbg.replay()</code> . If present, the method will also
compare the glucose fit vs the data.</li>
</ul>
<h3 id="output-parameter" tabindex="-1"><a class="header-anchor" href="#output-parameter"><span>Output parameter</span></a></h3>
<ul>
<li><code v-pre>analysis</code>: A dictionary containing the results of the analysis with fields <code v-pre>median</code>, <code v-pre>ci5th</code>, <code v-pre>ci25th</code>, <code v-pre>ci75th</code>,
<code v-pre>ci95th</code>, i.e., dictionaries containing the analysis results computed from the median, 5-th percentile, 25-th
percentile, 75-th percentile, and 95-th percentiles of the simulated profiles, respectively.
Remember that, if the adopted identification method is MAP or <code v-pre>n_replay=1</code>, the values contained in <code v-pre>median</code>, <code v-pre>ci5th</code>, <code v-pre>ci25th</code>, <code v-pre>ci75th</code>,
<code v-pre>ci95th</code> coincide. Each dictionary contains:
<ul>
<li><code v-pre>glucose</code> and <code v-pre>cgm</code>: two dictionaries containing the analysis results computed with AGATA from the simulated <code v-pre>glucose</code> and <code v-pre>cgm</code> profiles with fields:
<ul>
<li><code v-pre>variability</code>: a dictionary containing the following fields (corresponding to glucose variability indices):
<ul>
<li><code v-pre>mean_glucose</code>: the average glucose (mg/dl)</li>
<li><code v-pre>median_glucose</code>: the median of glucose (mg/dl)</li>
<li><code v-pre>std_glucose</code>: the glucose standard deviation (mg/dl)</li>
<li><code v-pre>cv_glucose</code>: the glucose coefficient of variation (%)</li>
<li><code v-pre>range_glucose</code>: the spanned glucose range (mg/dl)</li>
<li><code v-pre>iqr_glucose</code>: the glucose interquartile range (mg/dl)</li>
<li><code v-pre>auc_glucose</code>: the area under the glucose curve (mg^2/dl^2)</li>
<li><code v-pre>gmi</code>: the glucose management indicator (-)</li>
<li><code v-pre>cogi</code>: the continuous glucose monitoring index (-)</li>
<li><code v-pre>conga</code>: the CONGA index (-)</li>
<li><code v-pre>j_index</code>: the J-index (-)</li>
<li><code v-pre>mage_plus_index</code>: the positive MAGE index (mg/dl)</li>
<li><code v-pre>mage_minus_index</code>: the negative MAGE index (mg/dl)</li>
<li><code v-pre>mage_index</code>: the overall MAGE index (mg/dl)</li>
<li><code v-pre>ef_index</code>: the EF index (-)</li>
<li><code v-pre>modd</code>: the mean of daily difference (mg/dl)</li>
<li><code v-pre>sddm_index</code>: the standard deviation of daily means (mg/dl)</li>
<li><code v-pre>sdw_index</code>: the within standard deviation (mg/dl)</li>
<li><code v-pre>std_glucose_roc</code>: the standard deviation of glucose rat of change (mg/dl/min)</li>
<li><code v-pre>cvga</code>: the CVGA index (mg^2/dl^2)</li>
</ul>
</li>
<li><code v-pre>time_in_ranges</code>: a dictionary containing the following fields (corresponding to time in range indices):
<ul>
<li><code v-pre>time_in_target</code>: the time in target (%)</li>
<li><code v-pre>time_in_hypoglycemia</code>: the time in hypoglycemia (%)</li>
<li><code v-pre>time_in_l1_hypoglycemia</code>: the time in level 1 hypoglycemia (%)</li>
<li><code v-pre>time_in_l2_hypoglycemia</code>: the time in level 2 hypoglycemia (%)</li>
<li><code v-pre>time_in_hyperglycemia</code>: the time in hyperglycemia (%)</li>
<li><code v-pre>time_in_l1_hyperglycemia</code>: the time in level 1 hyperglycemia (%)</li>
<li><code v-pre>time_in_l2_hyperglycemia</code>: the time in level 2 hyperglycemia (%)</li>
</ul>
</li>
<li><code v-pre>risk</code>: a dictionary containing the following fields (corresponding to glucose risk indices):
<ul>
<li><code v-pre>adrr</code>: the average daily risk (-)</li>
<li><code v-pre>lbgi</code>: the low blood glucose index (-)</li>
<li><code v-pre>hbgi</code>: the high blood glucose index (-)</li>
<li><code v-pre>bgri</code>: the blood glucose risk index (-)</li>
<li><code v-pre>gri</code>: the glucose risk indicator (-)</li>
</ul>
</li>
<li><code v-pre>glycemic_transformation</code>: a dictionary containing the following fields (corresponding to glucose variability
indices which adopt a &quot;scale transformation&quot;):
<ul>
<li><code v-pre>grade_score</code>: the overall GRADE score (-)</li>
<li><code v-pre>grade_hypo_score</code>: the hypo GRADE score (-)</li>
<li><code v-pre>grade_hyper_score</code>: the hyper GRADE score (-)</li>
<li><code v-pre>grade_eu_score</code>: the euglycemia GRADE score (-)</li>
<li><code v-pre>igc</code>: the index of glucose control (-)</li>
<li><code v-pre>hypo_index</code>: the hypo index (-)</li>
<li><code v-pre>hyper_index</code>: the hyper index (-)</li>
<li><code v-pre>mr_index</code>: the MR index (-)</li>
</ul>
</li>
<li><code v-pre>events</code>: a dictionary containing the following fields (corresponding to glucose adverse events):
<ul>
<li><code v-pre>hypoglycemic_events</code>: a dictionary of dictionaries <code v-pre>hypo</code>, <code v-pre>l1</code>, and <code v-pre>l2</code> containing the results of the analysis
of hypoglycemic, level 1 hypoglycemic, and level 2 hypoglycemic events, respectively. Each dictionary has fields:
<ul>
<li><code v-pre>time_start</code>: a np.ndarray containing the timestamp when each event starts</li>
<li><code v-pre>time_end</code>: a np.ndarray containing the timestamp when each event ends</li>
<li><code v-pre>duration</code>: a np.ndarray containing the duration of each event (min)</li>
<li><code v-pre>mean_duration</code>: the average duration of the events (min)</li>
<li><code v-pre>events_per_week</code>: the frequency per week of the events (#/week)</li>
</ul>
</li>
<li><code v-pre>hyperglycemic_events</code>: a dictionary of dictionaries <code v-pre>hyper</code>, <code v-pre>l1</code>, and <code v-pre>l2</code> containing the results of the analysis
of hyperglycemic, level 1 hyperglycemic, and level 2 hyperglycemic events, respectively. Each dictionary has fields:
<ul>
<li><code v-pre>time_start</code>: a np.ndarray containing the timestamp when each event starts</li>
<li><code v-pre>time_end</code>: a np.ndarray containing the timestamp when each event ends</li>
<li><code v-pre>duration</code>: a np.ndarray containing the duration of each event (min)</li>
<li><code v-pre>mean_duration</code>: the average duration of the events (min)</li>
<li><code v-pre>events_per_week</code>: the frequency per week of the events (#/week)</li>
</ul>
</li>
<li><code v-pre>events</code>: a dictionary containing the following fields (corresponding to glucose adverse events):</li>
<li><code v-pre>extended_hypoglycemic_events</code>: a dictionary containing the results of the analysis
of extended hypoglycemic events with fields:
<ul>
<li><code v-pre>time_start</code>: a np.ndarray containing the timestamp when each event starts</li>
<li><code v-pre>time_end</code>: a np.ndarray containing the timestamp when each event ends</li>
<li><code v-pre>duration</code>: a np.ndarray containing the duration of each event (min)</li>
<li><code v-pre>mean_duration</code>: the average duration of the events (min)</li>
<li><code v-pre>events_per_week</code>: the frequency per week of the events (#/week)</li>
</ul>
</li>
</ul>
</li>
<li><code v-pre>data_quality</code>: a dictionary containing the following fields (corresponding to data quality):
<ul>
<li><code v-pre>number_of_days_of_observation</code>: the length of the profile (days)</li>
<li><code v-pre>missing_glucose_percentage</code>: the percentage of missing glucose data (%)</li>
</ul>
</li>
</ul>
</li>
<li><code v-pre>events</code>: a dictionary containing the analysis of the simulated meal/insulin events:
<ul>
<li><code v-pre>total_insulin</code>: the total amount of injected insulin (U)</li>
<li><code v-pre>total_basal_insulin</code>: the total amount of injected basal insulin (U)</li>
<li><code v-pre>total_bolus_insulin</code>: the total amount of injected bolus insulin (U)</li>
<li><code v-pre>total_correction_bolus_insulin</code>: the total amount of injected correction bolus  insulin (U)</li>
<li><code v-pre>total_cho</code>: the total amount of ingested meals (g)</li>
<li><code v-pre>total_hypotreatments</code>: the total amount of ingested hypotreatements (g)</li>
<li><code v-pre>total_meal_announcements</code>: the total amount of announced meals (g)</li>
<li><code v-pre>correction_bolus_insulin_number</code>: the number of correction bolus events (#)</li>
<li><code v-pre>hypotreatment_number</code>: the number of hypotreatment events (#)</li>
<li><code v-pre>exercise_session_number</code>: the number of exercise sessions (#). NOT YET IMPLEMENTED</li>
</ul>
</li>
</ul>
</li>
</ul>
<h3 id="example" tabindex="-1"><a class="header-anchor" href="#example"><span>Example</span></a></h3>
<div class="language-python line-numbers-mode" data-highlighter="prismjs" data-ext="py" data-title="py"><pre v-pre><code><span class="line"><span class="token comment"># Load previously saved results, e.g., ...</span></span>
<span class="line"><span class="token keyword">with</span> <span class="token builtin">open</span><span class="token punctuation">(</span>os<span class="token punctuation">.</span>path<span class="token punctuation">.</span>join<span class="token punctuation">(</span>results_folder_location<span class="token punctuation">,</span> <span class="token string">'results'</span><span class="token punctuation">,</span> <span class="token string">'workspaces'</span><span class="token punctuation">,</span> <span class="token string">'results.pkl'</span><span class="token punctuation">)</span><span class="token punctuation">,</span> <span class="token string">'rb'</span><span class="token punctuation">)</span> <span class="token keyword">as</span> <span class="token builtin">file</span><span class="token punctuation">:</span></span>
<span class="line">    replay_results <span class="token operator">=</span> pickle<span class="token punctuation">.</span>load<span class="token punctuation">(</span><span class="token builtin">file</span><span class="token punctuation">)</span></span>
<span class="line"></span>
<span class="line"><span class="token comment"># Analyze them</span></span>
<span class="line">analysis <span class="token operator">=</span> Analyzer<span class="token punctuation">.</span>analyze_replay_results<span class="token punctuation">(</span>replay_results<span class="token punctuation">)</span></span>
<span class="line"></span></code></pre>
<div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>The full code can be found in <code v-pre>/example/code/analysis_example.py</code>.</p>
<h2 id="analyzing-replay-results-from-portions-of-data-spanning-more-than-one-day-i-e-intervals" tabindex="-1"><a class="header-anchor" href="#analyzing-replay-results-from-portions-of-data-spanning-more-than-one-day-i-e-intervals"><span>Analyzing replay results from portions of data spanning more than one day (i.e., intervals)</span></a></h2>
<p>To analyze replay results from single portions of data use the <code v-pre>Analyzer.analyze_replay_results_interval()</code> static
method, which is formerly defined as:</p>
<div class="language-python line-numbers-mode" data-highlighter="prismjs" data-ext="py" data-title="py"><pre v-pre><code><span class="line">    <span class="token decorator annotation punctuation">@staticmethod</span></span>
<span class="line">    <span class="token keyword">def</span> <span class="token function">analyze_replay_results_interval</span><span class="token punctuation">(</span></span>
<span class="line">            replay_results_interval<span class="token punctuation">:</span> <span class="token builtin">list</span><span class="token punctuation">,</span></span>
<span class="line">            data_interval<span class="token punctuation">:</span> <span class="token builtin">list</span> <span class="token operator">=</span> <span class="token boolean">None</span><span class="token punctuation">,</span></span>
<span class="line">    <span class="token punctuation">)</span> <span class="token operator">-</span><span class="token operator">></span> Dict</span>
<span class="line"></span></code></pre>
<div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h3 id="input-parameters-1" tabindex="-1"><a class="header-anchor" href="#input-parameters-1"><span>Input parameters</span></a></h3>
<ul>
<li><code v-pre>replay_results_interval</code>: a list of dictionaries returned by or saved with the <code v-pre>rbg.replay()</code> method</li>
<li><code v-pre>data</code>, optional, default: <code v-pre>None</code>: The list of <code v-pre>data</code> parameter passed to <code v-pre>rbg.replay()</code> . If present, the method will also
compare the glucose fit vs the data.</li>
</ul>
<h3 id="output-parameter-1" tabindex="-1"><a class="header-anchor" href="#output-parameter-1"><span>Output parameter</span></a></h3>
<ul>
<li><code v-pre>analysis</code>: A dictionary containing the results of the analysis with fields <code v-pre>median</code>, <code v-pre>ci5th</code>, <code v-pre>ci25th</code>, <code v-pre>ci75th</code>,
<code v-pre>ci95th</code>, i.e., dictionaries containing the analysis results computed from the median, 5-th percentile, 25-th
percentile, 75-th percentile, and 95-th percentiles of the simulated profiles, respectively.
Remember that, if the adopted identification method is MAP or <code v-pre>n_replay=1</code>, the values contained in <code v-pre>median</code>, <code v-pre>ci5th</code>, <code v-pre>ci25th</code>, <code v-pre>ci75th</code>,
<code v-pre>ci95th</code> coincide. Each dictionary contains:
<ul>
<li><code v-pre>glucose</code> and <code v-pre>cgm</code>: two dictionaries containing the analysis results computed with AGATA from the simulated <code v-pre>glucose</code> and <code v-pre>cgm</code> profiles with fields:
<ul>
<li><code v-pre>variability</code>: a dictionary containing the following fields (corresponding to glucose variability indices):
<ul>
<li><code v-pre>mean_glucose</code>: the average glucose (mg/dl)</li>
<li><code v-pre>median_glucose</code>: the median of glucose (mg/dl)</li>
<li><code v-pre>std_glucose</code>: the glucose standard deviation (mg/dl)</li>
<li><code v-pre>cv_glucose</code>: the glucose coefficient of variation (%)</li>
<li><code v-pre>range_glucose</code>: the spanned glucose range (mg/dl)</li>
<li><code v-pre>iqr_glucose</code>: the glucose interquartile range (mg/dl)</li>
<li><code v-pre>auc_glucose</code>: the area under the glucose curve (mg^2/dl^2)</li>
<li><code v-pre>gmi</code>: the glucose management indicator (-)</li>
<li><code v-pre>cogi</code>: the continuous glucose monitoring index (-)</li>
<li><code v-pre>conga</code>: the CONGA index (-)</li>
<li><code v-pre>j_index</code>: the J-index (-)</li>
<li><code v-pre>mage_plus_index</code>: the positive MAGE index (mg/dl)</li>
<li><code v-pre>mage_minus_index</code>: the negative MAGE index (mg/dl)</li>
<li><code v-pre>mage_index</code>: the overall MAGE index (mg/dl)</li>
<li><code v-pre>ef_index</code>: the EF index (-)</li>
<li><code v-pre>modd</code>: the mean of daily difference (mg/dl)</li>
<li><code v-pre>sddm_index</code>: the standard deviation of daily means (mg/dl)</li>
<li><code v-pre>sdw_index</code>: the within standard deviation (mg/dl)</li>
<li><code v-pre>std_glucose_roc</code>: the standard deviation of glucose rat of change (mg/dl/min)</li>
<li><code v-pre>cvga</code>: the CVGA index (mg^2/dl^2)</li>
</ul>
</li>
<li><code v-pre>time_in_ranges</code>: a dictionary containing the following fields (corresponding to time in range indices):
<ul>
<li><code v-pre>time_in_target</code>: the time in target (%)</li>
<li><code v-pre>time_in_hypoglycemia</code>: the time in hypoglycemia (%)</li>
<li><code v-pre>time_in_l1_hypoglycemia</code>: the time in level 1 hypoglycemia (%)</li>
<li><code v-pre>time_in_l2_hypoglycemia</code>: the time in level 2 hypoglycemia (%)</li>
<li><code v-pre>time_in_hyperglycemia</code>: the time in hyperglycemia (%)</li>
<li><code v-pre>time_in_l1_hyperglycemia</code>: the time in level 1 hyperglycemia (%)</li>
<li><code v-pre>time_in_l2_hyperglycemia</code>: the time in level 2 hyperglycemia (%)</li>
</ul>
</li>
<li><code v-pre>risk</code>: a dictionary containing the following fields (corresponding to glucose risk indices):
<ul>
<li><code v-pre>adrr</code>: the average daily risk (-)</li>
<li><code v-pre>lbgi</code>: the low blood glucose index (-)</li>
<li><code v-pre>hbgi</code>: the high blood glucose index (-)</li>
<li><code v-pre>bgri</code>: the blood glucose risk index (-)</li>
<li><code v-pre>gri</code>: the glucose risk indicator (-)</li>
</ul>
</li>
<li><code v-pre>glycemic_transformation</code>: a dictionary containing the following fields (corresponding to glucose variability
indices which adopt a &quot;scale transformation&quot;):
<ul>
<li><code v-pre>grade_score</code>: the overall GRADE score (-)</li>
<li><code v-pre>grade_hypo_score</code>: the hypo GRADE score (-)</li>
<li><code v-pre>grade_hyper_score</code>: the hyper GRADE score (-)</li>
<li><code v-pre>grade_eu_score</code>: the euglycemia GRADE score (-)</li>
<li><code v-pre>igc</code>: the index of glucose control (-)</li>
<li><code v-pre>hypo_index</code>: the hypo index (-)</li>
<li><code v-pre>hyper_index</code>: the hyper index (-)</li>
<li><code v-pre>mr_index</code>: the MR index (-)</li>
</ul>
</li>
<li><code v-pre>events</code>: a dictionary containing the following fields (corresponding to glucose adverse events):
<ul>
<li><code v-pre>hypoglycemic_events</code>: a dictionary of dictionaries <code v-pre>hypo</code>, <code v-pre>l1</code>, and <code v-pre>l2</code> containing the results of the analysis
of hypoglycemic, level 1 hypoglycemic, and level 2 hypoglycemic events, respectively. Each dictionary has fields:
<ul>
<li><code v-pre>time_start</code>: a np.ndarray containing the timestamp when each event starts</li>
<li><code v-pre>time_end</code>: a np.ndarray containing the timestamp when each event ends</li>
<li><code v-pre>duration</code>: a np.ndarray containing the duration of each event (min)</li>
<li><code v-pre>mean_duration</code>: the average duration of the events (min)</li>
<li><code v-pre>events_per_week</code>: the frequency per week of the events (#/week)</li>
</ul>
</li>
<li><code v-pre>hyperglycemic_events</code>: a dictionary of dictionaries <code v-pre>hyper</code>, <code v-pre>l1</code>, and <code v-pre>l2</code> containing the results of the analysis
of hyperglycemic, level 1 hyperglycemic, and level 2 hyperglycemic events, respectively. Each dictionary has fields:
<ul>
<li><code v-pre>time_start</code>: a np.ndarray containing the timestamp when each event starts</li>
<li><code v-pre>time_end</code>: a np.ndarray containing the timestamp when each event ends</li>
<li><code v-pre>duration</code>: a np.ndarray containing the duration of each event (min)</li>
<li><code v-pre>mean_duration</code>: the average duration of the events (min)</li>
<li><code v-pre>events_per_week</code>: the frequency per week of the events (#/week)</li>
</ul>
</li>
<li><code v-pre>events</code>: a dictionary containing the following fields (corresponding to glucose adverse events):</li>
<li><code v-pre>extended_hypoglycemic_events</code>: a dictionary containing the results of the analysis
of extended hypoglycemic events with fields:
<ul>
<li><code v-pre>time_start</code>: a np.ndarray containing the timestamp when each event starts</li>
<li><code v-pre>time_end</code>: a np.ndarray containing the timestamp when each event ends</li>
<li><code v-pre>duration</code>: a np.ndarray containing the duration of each event (min)</li>
<li><code v-pre>mean_duration</code>: the average duration of the events (min)</li>
<li><code v-pre>events_per_week</code>: the frequency per week of the events (#/week)</li>
</ul>
</li>
</ul>
</li>
<li><code v-pre>data_quality</code>: a dictionary containing the following fields (corresponding to data quality):
<ul>
<li><code v-pre>number_of_days_of_observation</code>: the length of the profile (days)</li>
<li><code v-pre>missing_glucose_percentage</code>: the percentage of missing glucose data (%)</li>
</ul>
</li>
</ul>
</li>
<li><code v-pre>events</code>: a dictionary containing the analysis of the simulated meal/insulin events:
<ul>
<li><code v-pre>total_insulin</code>: the total amount of injected insulin (U)</li>
<li><code v-pre>total_basal_insulin</code>: the total amount of injected basal insulin (U)</li>
<li><code v-pre>total_bolus_insulin</code>: the total amount of injected bolus insulin (U)</li>
<li><code v-pre>total_correction_bolus_insulin</code>: the total amount of injected correction bolus  insulin (U)</li>
<li><code v-pre>total_cho</code>: the total amount of ingested meals (g)</li>
<li><code v-pre>total_hypotreatments</code>: the total amount of ingested hypotreatements (g)</li>
<li><code v-pre>total_meal_announcements</code>: the total amount of announced meals (g)</li>
<li><code v-pre>correction_bolus_insulin_number</code>: the number of correction bolus events (#)</li>
<li><code v-pre>hypotreatment_number</code>: the number of hypotreatment events (#)</li>
<li><code v-pre>exercise_session_number</code>: the number of exercise sessions (#). NOT YET IMPLEMENTED</li>
</ul>
</li>
</ul>
</li>
</ul>
<h3 id="example-1" tabindex="-1"><a class="header-anchor" href="#example-1"><span>Example</span></a></h3>
<div class="language-python line-numbers-mode" data-highlighter="prismjs" data-ext="py" data-title="py"><pre v-pre><code><span class="line"><span class="token comment"># Initialize results list</span></span>
<span class="line">replay_results_interval <span class="token operator">=</span> <span class="token punctuation">[</span><span class="token punctuation">]</span></span>
<span class="line"></span>
<span class="line"><span class="token comment"># Load previously saved results, e.g., ...</span></span>
<span class="line"><span class="token keyword">for</span> day <span class="token keyword">in</span> <span class="token builtin">range</span><span class="token punctuation">(</span>start_day<span class="token punctuation">,</span> end_day<span class="token operator">+</span><span class="token number">1</span><span class="token punctuation">)</span><span class="token punctuation">:</span></span>
<span class="line">    <span class="token keyword">with</span> <span class="token builtin">open</span><span class="token punctuation">(</span>os<span class="token punctuation">.</span>path<span class="token punctuation">.</span>join<span class="token punctuation">(</span>results_folder_location<span class="token punctuation">,</span> <span class="token string">'results'</span><span class="token punctuation">,</span> <span class="token string">'workspaces'</span><span class="token punctuation">,</span> <span class="token string">'results_'</span> <span class="token operator">+</span> <span class="token builtin">str</span><span class="token punctuation">(</span>day<span class="token punctuation">)</span> <span class="token operator">+</span> <span class="token string">'.pkl'</span><span class="token punctuation">)</span><span class="token punctuation">,</span> <span class="token string">'rb'</span><span class="token punctuation">)</span> <span class="token keyword">as</span> <span class="token builtin">file</span><span class="token punctuation">:</span></span>
<span class="line">        replay_results <span class="token operator">=</span> pickle<span class="token punctuation">.</span>load<span class="token punctuation">(</span><span class="token builtin">file</span><span class="token punctuation">)</span></span>
<span class="line">    replay_results_interval<span class="token punctuation">.</span>append<span class="token punctuation">(</span>replay_results<span class="token punctuation">)</span></span>
<span class="line"></span>
<span class="line"><span class="token comment"># Analyze them</span></span>
<span class="line">analysis <span class="token operator">=</span> Analyzer<span class="token punctuation">.</span>analyze_replay_results_interval<span class="token punctuation">(</span>replay_results_interval<span class="token operator">=</span>replay_results_interval<span class="token punctuation">)</span></span>
<span class="line"></span></code></pre>
<div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>The full code can be found in <code v-pre>/example/code/analysis_example_intervals.py</code>.</p>
</div></template>


