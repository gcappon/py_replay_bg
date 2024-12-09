<template><div><h1 id="replaying" tabindex="-1"><a class="header-anchor" href="#replaying"><span>Replaying</span></a></h1>
<p>Once created, we are finally ready to use the digital twins to run replay simulations.</p>
<p>The aims can be A LOT, e.g.:</p>
<ul>
<li>you want to simulate the impact of modulating the input data you used for twinning, e.g., reducing the insulin bolus
by 30%, and see what happens to glucose control</li>
<li>you want to evaluate the performance of a bolus calculator you developed</li>
<li>you want to develop a new algorithm for type 1 diabetes management</li>
<li>you want to find the best hypotreatment policy able to prevent hypoglycemia</li>
<li>you want to test an artificial pancreas algorithm</li>
<li>you just want to generate data using random insulin/meal inputs</li>
<li>and so on and so forth...</li>
</ul>
<p>In the following, we present how to use ReplayBG for running replay simulations and we will provide a comprehensive list
of its capabilities.</p>
<h2 id="the-replay-method" tabindex="-1"><a class="header-anchor" href="#the-replay-method"><span>The <code v-pre>replay</code> method</span></a></h2>
<p>Replay simulations in ReplayBG can be performed using the <code v-pre>replay</code> method of the <code v-pre>ReplayBG</code> object, which is formally
defined as:</p>
<div class="language-python line-numbers-mode" data-highlighter="prismjs" data-ext="py" data-title="py"><pre v-pre><code><span class="line">rbg<span class="token punctuation">.</span>replay<span class="token punctuation">(</span>data<span class="token punctuation">:</span> pd<span class="token punctuation">.</span>DataFrame<span class="token punctuation">,</span></span>
<span class="line">   bw<span class="token punctuation">:</span> <span class="token builtin">float</span><span class="token punctuation">,</span></span>
<span class="line">   save_name<span class="token punctuation">:</span> <span class="token builtin">str</span><span class="token punctuation">,</span></span>
<span class="line">   u2ss<span class="token punctuation">:</span> <span class="token builtin">float</span> <span class="token operator">|</span> <span class="token boolean">None</span> <span class="token operator">=</span> <span class="token boolean">None</span><span class="token punctuation">,</span></span>
<span class="line">   x0<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray <span class="token operator">|</span> <span class="token boolean">None</span> <span class="token operator">=</span> <span class="token boolean">None</span><span class="token punctuation">,</span></span>
<span class="line">   previous_data_name<span class="token punctuation">:</span> <span class="token builtin">str</span> <span class="token operator">|</span> <span class="token boolean">None</span>  <span class="token operator">=</span> <span class="token boolean">None</span><span class="token punctuation">,</span></span>
<span class="line">   twinning_method<span class="token punctuation">:</span> <span class="token builtin">str</span> <span class="token operator">=</span> <span class="token string">'mcmc'</span><span class="token punctuation">,</span></span>
<span class="line">   bolus_source<span class="token punctuation">:</span> <span class="token builtin">str</span> <span class="token operator">=</span> <span class="token string">'data'</span><span class="token punctuation">,</span></span>
<span class="line">   basal_source<span class="token punctuation">:</span> <span class="token builtin">str</span> <span class="token operator">=</span> <span class="token string">'data'</span><span class="token punctuation">,</span></span>
<span class="line">   cho_source<span class="token punctuation">:</span> <span class="token builtin">str</span> <span class="token operator">=</span> <span class="token string">'data'</span><span class="token punctuation">,</span></span>
<span class="line">   meal_generator_handler<span class="token punctuation">:</span> Callable <span class="token operator">=</span> default_meal_generator_handler<span class="token punctuation">,</span></span>
<span class="line">   meal_generator_handler_params<span class="token punctuation">:</span> Dict <span class="token operator">|</span> <span class="token boolean">None</span> <span class="token operator">=</span> <span class="token boolean">None</span><span class="token punctuation">,</span></span>
<span class="line">   bolus_calculator_handler<span class="token punctuation">:</span> Callable <span class="token operator">=</span> standard_bolus_calculator_handler<span class="token punctuation">,</span></span>
<span class="line">   bolus_calculator_handler_params<span class="token punctuation">:</span> Dict <span class="token operator">|</span> <span class="token boolean">None</span> <span class="token operator">=</span> <span class="token boolean">None</span><span class="token punctuation">,</span></span>
<span class="line">   basal_handler<span class="token punctuation">:</span> Callable <span class="token operator">=</span> default_basal_handler<span class="token punctuation">,</span></span>
<span class="line">   basal_handler_params<span class="token punctuation">:</span> Dict <span class="token operator">|</span> <span class="token boolean">None</span> <span class="token operator">=</span> <span class="token boolean">None</span><span class="token punctuation">,</span></span>
<span class="line">   enable_hypotreatments<span class="token punctuation">:</span> <span class="token builtin">bool</span> <span class="token operator">=</span> <span class="token boolean">False</span><span class="token punctuation">,</span></span>
<span class="line">   hypotreatments_handler<span class="token punctuation">:</span> Callable <span class="token operator">=</span> ada_hypotreatments_handler<span class="token punctuation">,</span></span>
<span class="line">   hypotreatments_handler_params<span class="token punctuation">:</span> Dict <span class="token operator">|</span> <span class="token boolean">None</span> <span class="token operator">=</span> <span class="token boolean">None</span><span class="token punctuation">,</span></span>
<span class="line">   enable_correction_boluses<span class="token punctuation">:</span> <span class="token builtin">bool</span> <span class="token operator">=</span> <span class="token boolean">False</span><span class="token punctuation">,</span></span>
<span class="line">   correction_boluses_handler<span class="token punctuation">:</span> Callable <span class="token operator">=</span> corrects_above_250_handler<span class="token punctuation">,</span></span>
<span class="line">   correction_boluses_handler_params<span class="token punctuation">:</span> Dict <span class="token operator">|</span> <span class="token boolean">None</span> <span class="token operator">=</span> <span class="token boolean">None</span><span class="token punctuation">,</span></span>
<span class="line">   save_suffix<span class="token punctuation">:</span> <span class="token builtin">str</span> <span class="token operator">=</span> <span class="token string">''</span><span class="token punctuation">,</span></span>
<span class="line">   save_workspace<span class="token punctuation">:</span> <span class="token builtin">bool</span> <span class="token operator">=</span> <span class="token boolean">False</span><span class="token punctuation">,</span></span>
<span class="line">   n_replay<span class="token punctuation">:</span> <span class="token builtin">int</span> <span class="token operator">=</span> <span class="token number">1000</span><span class="token punctuation">,</span></span>
<span class="line">   sensors<span class="token punctuation">:</span> <span class="token builtin">list</span> <span class="token operator">|</span> <span class="token boolean">None</span> <span class="token operator">=</span> <span class="token boolean">None</span></span>
<span class="line"><span class="token punctuation">)</span> <span class="token operator">-</span><span class="token operator">></span> Dict<span class="token punctuation">:</span></span>
<span class="line"></span></code></pre>
<div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h3 id="input-parameters" tabindex="-1"><a class="header-anchor" href="#input-parameters"><span>Input parameters</span></a></h3>
<ul>
<li><code v-pre>data</code>: A Pandas dataframe which contains the data to be used by the tool. For more information on <code v-pre>data</code> format and
requirements see <RouteLink to="/documentation/data_requirements.html">Data Requirements</RouteLink> page.</li>
<li><code v-pre>bw</code>: A float representing the patient's body weight in kg.</li>
<li><code v-pre>save_name</code>: A string used to label, thus identify, each output file and result. This MUST correspond to the <code v-pre>save_name</code>
string provided to the <code v-pre>twin</code> method during twinning.</li>
<li><code v-pre>u2ss</code>, optional, default: <code v-pre>None</code>: A float representing the steady state of the basal insulin infusion (e.g., the
average basal insulin) in mU/(kg*min). If <code v-pre>None</code>, it will be set to the average of the basal insulin in input. This MUST
correspond to the <code v-pre>u2ss</code> value provided to the <code v-pre>twin</code> method during twinning.</li>
<li><code v-pre>x0</code>, optional, default: <code v-pre>None</code>: An np.ndarray, containing the initial model conditions. If <code v-pre>None</code>, the model will
start to the default steady state.</li>
<li><code v-pre>previous_data_name</code>, optional, default: <code v-pre>None</code>: A string representing the name of the previous data portion.
This is used to correcly &quot;transfer&quot; the initial model conditions to the current portion of data. Practically, this is
equal to the <code v-pre>save_name</code> used during the creation of the digital twin related to the previous portion of data. It must
be set if <code v-pre>x0</code> is not <code v-pre>None</code>.</li>
<li><code v-pre>twinning_method</code>, optional, <code v-pre>{'mcmc', 'map'}</code>, default: <code v-pre>'mcmc'</code>: A string used to select the method to be used to
twin the model. This MUST correspond to the <code v-pre>twinning_method</code> value provided to the <code v-pre>twin</code> method during twinning.</li>
<li><code v-pre>bolus_source</code>, optional, {<code v-pre>'data'</code>, <code v-pre>'dss'</code>}, default: <code v-pre>'data'</code>: A string defining whether to use, during replay,
the insulin bolus data contained in the <code v-pre>'data'</code> dataframe (if <code v-pre>'data'</code>), or the boluses generated by the bolus
calculator implemented via the provided <code v-pre>'bolusCalculatorHandler'</code> function.</li>
<li><code v-pre>basal_source</code>, optional, {<code v-pre>'data'</code>, <code v-pre>'u2ss'</code>, <code v-pre>'dss'</code>}, default: <code v-pre>'data'</code>: A string defining whether to use,</li>
<li>during replay, the insulin basal data contained in the <code v-pre>'data'</code> dataframe (if <code v-pre>'data'</code>), or the basal generated by
the controller implemented via the provided <code v-pre>'basalControllerHandler'</code> function (if <code v-pre>'dss'</code>), or fixed to the average
basal rate used during twinning (if <code v-pre>'u2ss'</code>).</li>
<li><code v-pre>cho_source</code>, optional, {<code v-pre>'data'</code>, <code v-pre>'generated'</code>}, default: <code v-pre>'data'</code>: A string defining whether to use, during replay,
the CHO data contained in the <code v-pre>'data'</code> dataframe (if <code v-pre>'data'</code>), or the CHO generated by the meal generator</li>
<li>implemented via the provided <code v-pre>'mealGeneratorHandler'</code> function (if <code v-pre>'generated'</code>).</li>
<li><code v-pre>meal_generator_handler</code>, optional, default: <code v-pre>default_meal_generator_handler</code>: A callback function that implements
a meal generator to be used during the replay simulation. For more information see the below
<a href="#event-handlers">Event handlers</a> section.</li>
<li><code v-pre>meal_generator_handler_params</code>, optional, default: <code v-pre>None</code>: A Python dictionary that contains the parameters to pass
to the <code v-pre>meal_generator_handler</code> function. It also serves as memory area for the <code v-pre>meal_generator_handler</code> function.
For more information see the below <a href="#event-handlers">Event handlers</a> section.</li>
<li><code v-pre>bolus_calculator_handler</code>, optional, default : <code v-pre>standard_bolus_calculator_handler</code>: A callback function that
implements a bolus calculator to be used during the replay simulation. For more information see the
below <a href="#event-handlers">Event handlers</a> section.</li>
<li><code v-pre>bolus_calculator_handler_params</code>, optional, default: <code v-pre>None</code>: A Python dictionary that contains the parameters to pass
to the <code v-pre>bolusCalculatorHandler</code> function. It also serves as memory area for the <code v-pre>bolusCalculatorHandler</code> function.
For more information see the below <a href="#event-handlers">Event handlers</a> section.</li>
<li><code v-pre>basal_handler</code>, optional, default: <code v-pre>default_basal_handler</code>: A callback function that implements a basal controller
to be used during the replay simulation. For more information see the
below <a href="#event-handlers">Event handlers</a> section.</li>
<li><code v-pre>basal_handler_params</code>, optional, default: <code v-pre>None</code>: A Python dictionary that contains the parameters to pass to the
<code v-pre>basalHandler</code> function. It also serves as memory area for the <code v-pre>basalHandler</code> function. For more information see the below
<a href="#event-handlers">Event handlers</a> section.</li>
<li><code v-pre>enable_hypotreatments</code>, optional, default: <code v-pre>False</code>: A boolean that specifies whether to enable hypotreatments
during the replay simulation. For more information see the below <a href="#event-handlers">Event handlers</a> section.</li>
<li><code v-pre>hypotreatments_handler</code>, optional, default: <code v-pre>ada_hypotreatments_handler</code>: A callback function that implements a
hypotreatment strategy during the replay simulation. For more information see the below
<a href="#event-handlers">Event handlers</a> section.</li>
<li><code v-pre>hypotreatments_handler_params</code>, optional, default: <code v-pre>None</code>: A Python dictionary that contains the parameters to
pass to the <code v-pre>hypoTreatmentsHandler</code> function. It also serves as memory area for the <code v-pre>hypoTreatmentsHandler</code>
function. For more information see the below <a href="#event-handlers">Event handlers</a> section.</li>
<li><code v-pre>enable_correction_boluses</code>, optional, default: <code v-pre>False</code>: A boolean that specifies whether to enable correction
boluses during the replay simulation. For more information see the below <a href="#event-handlers">Event handlers</a> section.</li>
<li><code v-pre>correction_boluses_handler</code>, optional, default: <code v-pre>corrects_above_250_handler</code>: A callback function that
implements a corrective bolus strategy during the replay simulation. For more information see the below
<a href="#event-handlers">Event handlers</a> section.</li>
<li><code v-pre>correction_boluses_handler_params</code>, optional, default: <code v-pre>None</code>: A Python dictionary that contains the parameters
to pass to the <code v-pre>correctionBolusesHandler</code> function. It also serves as memory area for the <code v-pre>correctionBolusesHandler</code>
function. For more information see the below <a href="#event-handlers">Event handlers</a> section.</li>
<li><code v-pre>save_suffix</code>, optional, default: <code v-pre>''</code>: A string to be attached as suffix to the resulting output files' name.</li>
<li><code v-pre>save_workspace</code>, optional, default: <code v-pre>False</code>: A boolean that specifies whether to save the results of the simulation
in the <code v-pre>results/workspaces</code> folder or not.</li>
<li><code v-pre>n_replay</code>, optional, {1, 10, 100, 1000}, default: <code v-pre>1000</code>: A number to select the sampled form to be used for the
replay simulations. Ignored if twinning_method is 'map'.</li>
<li><code v-pre>sensors</code>: , optional, default: <code v-pre>None</code>: A <code v-pre>list[Sensors]</code> to be used in each of the replay simulations. Its length
must coincide with the selected <code v-pre>n_replay</code>. Used when working with intervals. If <code v-pre>None</code> new sensors will be used.</li>
</ul>
<div class="hint-container tip">
<p class="hint-container-title">REMEMBER</p>
<p>The total length of the simulation, <code v-pre>simulation_length</code>, is defined in minutes and determined by ReplayBG automatically
using the <code v-pre>t</code> column of <code v-pre>data</code> and the <code v-pre>yts</code> input parameter provided to the <code v-pre>ReplayBG</code> object builder.</p>
<p>For example, if <code v-pre>yts</code> is <code v-pre>5</code> minutes and <code v-pre>t</code> starts from <code v-pre>20-Dec-2013 10:36:00</code> and ends to <code v-pre>20-Dec-2013 10:46:00</code>,
then <code v-pre>simulation_length</code> will be <code v-pre>10</code>.</p>
</div>
<div class="hint-container warning">
<p class="hint-container-title">Warning</p>
<p>The <code v-pre>replay</code> method will generate an error if the digital twin has not been created first.</p>
</div>
<h2 id="simulation-results" tabindex="-1"><a class="header-anchor" href="#simulation-results"><span>Simulation results</span></a></h2>
<p>The <code v-pre>replay</code> method will return the simulation results in the form of a dictionary with the following fields:</p>
<ul>
<li><code v-pre>glucose</code>: a dictionary containing the simulated plasma glucose timeseries (mg/dl). It contains:
<ul>
<li><code v-pre>realizations</code>: a np.ndarray of size (<code v-pre>n_replay</code>, <code v-pre>simulation_length</code>) containing each <code v-pre>n_replay</code> simulated
glucose profile</li>
<li><code v-pre>median</code>: a np.ndarray of size (<code v-pre>simulation_length</code>, ) containing the median simulated glucose profile (obtained
from <code v-pre>realizations</code>)</li>
<li><code v-pre>ci25th</code>: a np.ndarray of size (<code v-pre>simulation_length</code>, ) containing the simulated glucose profile corresponding to the
25th percentile (obtained from <code v-pre>realizations</code>)</li>
<li><code v-pre>ci75th</code>: a np.ndarray of size (<code v-pre>simulation_length</code>, ) containing the simulated glucose profile corresponding to the
75th percentile (obtained from <code v-pre>realizations</code>)</li>
<li><code v-pre>ci5th</code>: a np.ndarray of size (<code v-pre>simulation_length</code>, ) containing the simulated glucose profile corresponding to the
5th percentile (obtained from <code v-pre>realizations</code>)</li>
<li><code v-pre>ci95th</code>: a np.ndarray of size (<code v-pre>simulation_length</code>, ) containing the simulated glucose profile corresponding to the
95th percentile (obtained from <code v-pre>realizations</code>)</li>
</ul>
</li>
<li><code v-pre>cgm</code>: a dictionary containing the simulated CGM timeseries (mg/dl). It contains:
<ul>
<li><code v-pre>realizations</code>: a np.ndarray of size (<code v-pre>n_replay</code>, <code v-pre>simulation_length/yts</code>) containing each <code v-pre>n_replay</code> simulated
cgm profile</li>
<li><code v-pre>median</code>: a np.ndarray of size (<code v-pre>simulation_length/yts</code>, ) containing the median simulated cgm profile (obtained
from <code v-pre>realizations</code>)</li>
<li><code v-pre>ci25th</code>: a np.ndarray of size (<code v-pre>simulation_length/yts</code>, ) containing the simulated cgm profile corresponding to the
25th percentile (obtained from <code v-pre>realizations</code>)</li>
<li><code v-pre>ci75th</code>: a np.ndarray of size (<code v-pre>simulation_length/yts</code>, ) containing the simulated cgm profile corresponding to the
75th percentile (obtained from <code v-pre>realizations</code>)</li>
<li><code v-pre>ci5th</code>: a np.ndarray of size (<code v-pre>simulation_length/yts</code>, ) containing the simulated cgm profile corresponding to the
5th percentile (obtained from <code v-pre>realizations</code>)</li>
<li><code v-pre>ci95th</code>: a np.ndarray of size (<code v-pre>simulation_length/yts</code>, ) containing the simulated cgm profile corresponding to the
95th percentile (obtained from <code v-pre>realizations</code>)</li>
</ul>
</li>
<li><code v-pre>x_end</code>: a dictionary containing the final model conditions (to be used when working with intervals). It contains:
<ul>
<li><code v-pre>realizations</code>: a np.ndarray of size (<code v-pre>n_replay</code>, <code v-pre>n_model_equations</code>) containing for each <code v-pre>n_replay</code> the final state
of the model. <code v-pre>n_model_equations</code> is different depending on the blueprint.</li>
</ul>
</li>
<li><code v-pre>insulin_bolus</code>: a dictionary containing the administered insulin boluses during the replay simulation (U/min). It contains:
<ul>
<li><code v-pre>realizations</code>: a np.ndarray of size (<code v-pre>n_replay</code>, <code v-pre>simulation_length</code>) containing the <code v-pre>n_replay</code> simulated series
of administered insulin boluses</li>
</ul>
</li>
<li><code v-pre>correction_bolus</code>: a dictionary containing the administered corrective insulin boluses during the replay simulation (U/min). It contains:
<ul>
<li><code v-pre>realizations</code>: a np.ndarray of size (<code v-pre>n_replay</code>, <code v-pre>simulation_length</code>) containing the <code v-pre>n_replay</code> simulated series
of administered corrective insulin boluses</li>
</ul>
</li>
<li><code v-pre>insulin_basal</code>: a dictionary containing the administered basal insulin during the replay simulation (U/min). It contains:
<ul>
<li><code v-pre>realizations</code>: a np.ndarray of size (<code v-pre>n_replay</code>, <code v-pre>simulation_length</code>) containing the <code v-pre>n_replay</code> simulated series
of administered basal insulin</li>
</ul>
</li>
<li><code v-pre>cho</code>: a dictionary containing the meal intakes had during the replay simulation (g/min). It contains:
<ul>
<li><code v-pre>realizations</code>: a np.ndarray of size (<code v-pre>n_replay</code>, <code v-pre>simulation_length</code>) containing the <code v-pre>n_replay</code> simulated series
of meal intakes</li>
</ul>
</li>
<li><code v-pre>hypotreatments</code>: a dictionary containing the hypotreatment intakes had during the replay simulation (g/min). It contains:
<ul>
<li><code v-pre>realizations</code>: a np.ndarray of size (<code v-pre>n_replay</code>, <code v-pre>simulation_length</code>) containing the <code v-pre>n_replay</code> simulated series
of hypotreatment intakes</li>
</ul>
</li>
<li><code v-pre>meal_announcment</code>: a dictionary containing the announced CHO intakes had during the replay simulation (g). It contains:
<ul>
<li><code v-pre>realizations</code>: a np.ndarray of size (<code v-pre>n_replay</code>, <code v-pre>simulation_length</code>) containing the <code v-pre>n_replay</code> simulated series
of announced CHO intakes</li>
</ul>
</li>
<li><code v-pre>vo2</code>: a dictionary containing the input exercise VO2 used during the replay simulation (-) (NOT YET IMPLEMENTED). It contains:
<ul>
<li><code v-pre>realizations</code>: a np.ndarray of size (<code v-pre>n_replay</code>, <code v-pre>simulation_length</code>) containing the <code v-pre>n_replay</code> simulated series
of exercise VO2</li>
</ul>
</li>
<li><code v-pre>sensors</code>: a list of <code v-pre>Sensors</code> objects of size (<code v-pre>n_replay</code>) (to be used when working with intervals).</li>
<li><code v-pre>rbg_data</code>: the given <code v-pre>data</code> but in a proprietary <code v-pre>ReplayBGData</code> format (to be used for debugging).</li>
<li><code v-pre>model</code>: the model used for simulation (to be used for debugging).</li>
</ul>
<div class="hint-container tip">
<p class="hint-container-title">Tips</p>
<p>Beside returning the above dictionary, if the <code v-pre>save_workspace</code> is set to <code v-pre>True</code>, ReplayBG will
also save it in a <code v-pre>.pkl</code> file using <code v-pre>save_name</code> and <code v-pre>save_suffix</code> parameters to save it as:
<code v-pre>results/workspaces/&lt;save_name&gt;_&lt;save_suffix&gt;.pkl</code>.</p>
</div>
<h2 id="replaying-single-portions-of-data" tabindex="-1"><a class="header-anchor" href="#replaying-single-portions-of-data"><span>Replaying single portions of data</span></a></h2>
<p>To replay single portions of data, i.e., a single meal event or a single day, you can follow this example, which shows how
to use a digital twin previously created using the MCMC twinning method (stored in <code v-pre>results/mcmc/example.pkl</code>).
In this example, we will just simulate a reduction of 20% of the original insulin boluses:</p>
<div class="language-python line-numbers-mode" data-highlighter="prismjs" data-ext="py" data-title="py"><pre v-pre><code><span class="line"><span class="token keyword">import</span> os</span>
<span class="line"></span>
<span class="line"><span class="token keyword">from</span> py_replay_bg<span class="token punctuation">.</span>py_replay_bg <span class="token keyword">import</span> ReplayBG</span>
<span class="line"></span>
<span class="line"></span>
<span class="line"><span class="token comment"># Set verbosity</span></span>
<span class="line">verbose <span class="token operator">=</span> <span class="token boolean">True</span></span>
<span class="line">plot_mode <span class="token operator">=</span> <span class="token boolean">False</span></span>
<span class="line"></span>
<span class="line"><span class="token comment"># Set other parameters for twinning</span></span>
<span class="line">blueprint <span class="token operator">=</span> <span class="token string">'multi-meal'</span></span>
<span class="line">save_folder <span class="token operator">=</span> os<span class="token punctuation">.</span>path<span class="token punctuation">.</span>join<span class="token punctuation">(</span>os<span class="token punctuation">.</span>path<span class="token punctuation">.</span>abspath<span class="token punctuation">(</span><span class="token string">''</span><span class="token punctuation">)</span><span class="token punctuation">)</span></span>
<span class="line"></span>
<span class="line"><span class="token comment"># Set bw and u2ss</span></span>
<span class="line">bw <span class="token operator">=</span> <span class="token punctuation">.</span><span class="token punctuation">.</span><span class="token punctuation">.</span> <span class="token comment"># Set bw</span></span>
<span class="line">u2ss <span class="token operator">=</span> <span class="token punctuation">.</span><span class="token punctuation">.</span><span class="token punctuation">.</span> <span class="token comment">#u2ss</span></span>
<span class="line"></span>
<span class="line"><span class="token comment"># Instantiate ReplayBG</span></span>
<span class="line">rbg <span class="token operator">=</span> ReplayBG<span class="token punctuation">(</span>blueprint<span class="token operator">=</span>blueprint<span class="token punctuation">,</span> save_folder<span class="token operator">=</span>save_folder<span class="token punctuation">,</span></span>
<span class="line">               yts<span class="token operator">=</span><span class="token number">5</span><span class="token punctuation">,</span> exercise<span class="token operator">=</span><span class="token boolean">False</span><span class="token punctuation">,</span></span>
<span class="line">               seed<span class="token operator">=</span><span class="token number">1</span><span class="token punctuation">,</span></span>
<span class="line">               verbose<span class="token operator">=</span>verbose<span class="token punctuation">,</span> plot_mode<span class="token operator">=</span>plot_mode<span class="token punctuation">)</span></span>
<span class="line"></span>
<span class="line"><span class="token comment"># Load data and set save_name</span></span>
<span class="line">data <span class="token operator">=</span> <span class="token punctuation">.</span><span class="token punctuation">.</span><span class="token punctuation">.</span> </span>
<span class="line">save_name <span class="token operator">=</span> <span class="token string">'example'</span></span>
<span class="line"></span>
<span class="line"><span class="token comment"># Reduce the original boluses by 20%</span></span>
<span class="line">data<span class="token punctuation">.</span>bolus <span class="token operator">=</span> data<span class="token punctuation">.</span>bolus <span class="token operator">*</span> <span class="token number">0.8</span></span>
<span class="line"></span>
<span class="line"><span class="token comment"># Replay the twin using the modified data</span></span>
<span class="line">replay_results <span class="token operator">=</span> rbg<span class="token punctuation">.</span>replay<span class="token punctuation">(</span>data<span class="token operator">=</span>data<span class="token punctuation">,</span> bw<span class="token operator">=</span>bw<span class="token punctuation">,</span> save_name<span class="token operator">=</span>save_name<span class="token punctuation">,</span></span>
<span class="line">                            n_replay<span class="token operator">=</span><span class="token number">10</span><span class="token punctuation">,</span></span>
<span class="line">                            twinning_method<span class="token operator">=</span><span class="token string">'mcmc'</span><span class="token punctuation">,</span></span>
<span class="line">                            save_workspace<span class="token operator">=</span><span class="token boolean">True</span><span class="token punctuation">,</span></span>
<span class="line">                            u2ss<span class="token operator">=</span>u2ss<span class="token punctuation">,</span></span>
<span class="line">                            save_suffix<span class="token operator">=</span><span class="token string">'reduced'</span><span class="token punctuation">)</span></span>
<span class="line"></span></code></pre>
<div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>The results will be saved in
<code v-pre>&lt;save_folder&gt;/results/workspaces/example_reduced.pkl</code>.</p>
<p>A fully working example can be found in <code v-pre>example/code/replay_mcmc.py</code>.</p>
<div class="hint-container tip">
<p class="hint-container-title">Tips</p>
<p>To do the same but using a digital twin created with the MAP twinning method, just set <code v-pre>twinning_method</code> to <code v-pre>'map'</code>.
A full example can be found in <code v-pre>example/code/replay_map.py</code>.</p>
</div>
<h2 id="replaying-portions-of-data-spanning-more-than-one-day-i-e-intervals" tabindex="-1"><a class="header-anchor" href="#replaying-portions-of-data-spanning-more-than-one-day-i-e-intervals"><span>Replaying portions of data spanning more than one day (i.e., intervals)</span></a></h2>
<p>To replay portions of data than span multiple days, i.e., an intervals, you need to practically do the following steps:</p>
<ol>
<li>initialize empty initial conditions, i.e., <code v-pre>x0</code>, <code v-pre>previous_data_name</code>, <code v-pre>sensors</code>.</li>
<li>replay the first day</li>
<li>extract from the results <code v-pre>x0</code>, <code v-pre>previous_data_name</code>, <code v-pre>sensors</code> to be used for the next day</li>
<li>replay the subsequent day
5repeat steps 3 and 4, for each subsequent day of the interval.</li>
</ol>
<p>To implement these steps you can follow this example, which shows how to replay an interval spanning two days
using two digital twins previously created using the MCMC twinning method (stored in <code v-pre>results/mcmc/example_1.pkl</code> and
<code v-pre>results/mcmc/example_2.pkl</code>).
In this example, we will just simulate the original insulin boluses:</p>
<div class="language-python line-numbers-mode" data-highlighter="prismjs" data-ext="py" data-title="py"><pre v-pre><code><span class="line"><span class="token keyword">import</span> os</span>
<span class="line"></span>
<span class="line"><span class="token keyword">from</span> py_replay_bg<span class="token punctuation">.</span>py_replay_bg <span class="token keyword">import</span> ReplayBG</span>
<span class="line"></span>
<span class="line"><span class="token comment"># Set verbosity</span></span>
<span class="line">verbose <span class="token operator">=</span> <span class="token boolean">True</span></span>
<span class="line">plot_mode <span class="token operator">=</span> <span class="token boolean">False</span></span>
<span class="line"></span>
<span class="line"><span class="token comment"># Set other parameters for twinning</span></span>
<span class="line">blueprint <span class="token operator">=</span> <span class="token string">'multi-meal'</span></span>
<span class="line">save_folder <span class="token operator">=</span> os<span class="token punctuation">.</span>path<span class="token punctuation">.</span>join<span class="token punctuation">(</span>os<span class="token punctuation">.</span>path<span class="token punctuation">.</span>abspath<span class="token punctuation">(</span><span class="token string">''</span><span class="token punctuation">)</span><span class="token punctuation">)</span></span>
<span class="line"></span>
<span class="line"><span class="token comment"># Set bw and u2ss</span></span>
<span class="line">bw <span class="token operator">=</span> <span class="token punctuation">.</span><span class="token punctuation">.</span><span class="token punctuation">.</span></span>
<span class="line">u2ss <span class="token operator">=</span> <span class="token punctuation">.</span><span class="token punctuation">.</span><span class="token punctuation">.</span></span>
<span class="line"></span>
<span class="line">x0 <span class="token operator">=</span> <span class="token boolean">None</span></span>
<span class="line">previous_data_name <span class="token operator">=</span> <span class="token boolean">None</span></span>
<span class="line">sensors <span class="token operator">=</span> <span class="token boolean">None</span></span>
<span class="line"></span>
<span class="line"><span class="token comment"># Initialize the list of results</span></span>
<span class="line">replay_results_interval <span class="token operator">=</span> <span class="token punctuation">[</span><span class="token punctuation">]</span></span>
<span class="line">data_interval <span class="token operator">=</span> <span class="token punctuation">[</span><span class="token punctuation">]</span></span>
<span class="line"></span>
<span class="line"><span class="token comment"># Instantiate ReplayBG</span></span>
<span class="line">rbg <span class="token operator">=</span> ReplayBG<span class="token punctuation">(</span>blueprint<span class="token operator">=</span>blueprint<span class="token punctuation">,</span> save_folder<span class="token operator">=</span>save_folder<span class="token punctuation">,</span></span>
<span class="line">               yts<span class="token operator">=</span><span class="token number">5</span><span class="token punctuation">,</span> exercise<span class="token operator">=</span><span class="token boolean">False</span><span class="token punctuation">,</span></span>
<span class="line">               seed<span class="token operator">=</span><span class="token number">1</span><span class="token punctuation">,</span></span>
<span class="line">               verbose<span class="token operator">=</span>verbose<span class="token punctuation">,</span> plot_mode<span class="token operator">=</span>plot_mode<span class="token punctuation">)</span></span>
<span class="line"></span>
<span class="line"><span class="token comment"># Set interval to twin</span></span>
<span class="line">start_day <span class="token operator">=</span> <span class="token number">1</span></span>
<span class="line">end_day <span class="token operator">=</span> <span class="token number">2</span></span>
<span class="line"></span>
<span class="line"><span class="token comment"># Twin the interval</span></span>
<span class="line"><span class="token keyword">for</span> day <span class="token keyword">in</span> <span class="token builtin">range</span><span class="token punctuation">(</span>start_day<span class="token punctuation">,</span> end_day<span class="token operator">+</span><span class="token number">1</span><span class="token punctuation">)</span><span class="token punctuation">:</span></span>
<span class="line"></span>
<span class="line">    <span class="token comment"># Load data and set save_name</span></span>
<span class="line">    data <span class="token operator">=</span> <span class="token punctuation">.</span><span class="token punctuation">.</span><span class="token punctuation">.</span></span>
<span class="line">    save_name <span class="token operator">=</span> <span class="token string">'example'</span> <span class="token operator">+</span> <span class="token builtin">str</span><span class="token punctuation">(</span>day<span class="token punctuation">)</span></span>
<span class="line"></span>
<span class="line">    <span class="token comment"># Replay the twin with the same input data to get the initial conditions for the subsequent day</span></span>
<span class="line">    replay_results <span class="token operator">=</span> rbg<span class="token punctuation">.</span>replay<span class="token punctuation">(</span>data<span class="token operator">=</span>data<span class="token punctuation">,</span> bw<span class="token operator">=</span>bw<span class="token punctuation">,</span> save_name<span class="token operator">=</span>save_name<span class="token punctuation">,</span></span>
<span class="line">                                twinning_method<span class="token operator">=</span><span class="token string">'mcmc'</span><span class="token punctuation">,</span></span>
<span class="line">                                n_replay<span class="token operator">=</span><span class="token number">100</span><span class="token punctuation">,</span></span>
<span class="line">                                save_workspace<span class="token operator">=</span><span class="token boolean">True</span><span class="token punctuation">,</span></span>
<span class="line">                                x0<span class="token operator">=</span>x0<span class="token punctuation">,</span> u2ss<span class="token operator">=</span>u2ss<span class="token punctuation">,</span> previous_data_name<span class="token operator">=</span>previous_data_name<span class="token punctuation">,</span> sensors<span class="token operator">=</span>sensors<span class="token punctuation">,</span></span>
<span class="line">                                save_suffix<span class="token operator">=</span><span class="token string">'_intervals'</span><span class="token punctuation">)</span></span>
<span class="line"></span>
<span class="line">    <span class="token comment"># Append results</span></span>
<span class="line">    replay_results_interval<span class="token punctuation">.</span>append<span class="token punctuation">(</span>replay_results<span class="token punctuation">)</span></span>
<span class="line">    data_interval<span class="token punctuation">.</span>append<span class="token punctuation">(</span>data<span class="token punctuation">)</span></span>
<span class="line"></span>
<span class="line">    <span class="token comment"># Set initial conditions for next day equal to the "ending conditions" of the current day</span></span>
<span class="line">    x0 <span class="token operator">=</span> replay_results<span class="token punctuation">[</span><span class="token string">'x_end'</span><span class="token punctuation">]</span><span class="token punctuation">[</span><span class="token string">'realizations'</span><span class="token punctuation">]</span><span class="token punctuation">[</span><span class="token number">0</span><span class="token punctuation">]</span><span class="token punctuation">.</span>tolist<span class="token punctuation">(</span><span class="token punctuation">)</span></span>
<span class="line"></span>
<span class="line">    <span class="token comment"># Set sensors to use the same sensors during the next portion of data</span></span>
<span class="line">    sensors <span class="token operator">=</span> replay_results<span class="token punctuation">[</span><span class="token string">'sensors'</span><span class="token punctuation">]</span></span>
<span class="line"></span>
<span class="line">    <span class="token comment"># Set previous_data_name</span></span>
<span class="line">    previous_data_name <span class="token operator">=</span> save_name</span>
<span class="line"></span></code></pre>
<div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>The results will be saved in <code v-pre>&lt;save_folder&gt;/results/workspaces/example_1_intervals.pkl</code> and
<code v-pre>&lt;save_folder&gt;/results/workspaces/example_2_intervals.pkl</code>.</p>
<p>A fully working example can be found in <code v-pre>example/code/replay_intervals_mcmc.py</code>.</p>
<div class="hint-container tip">
<p class="hint-container-title">Tips</p>
<p>To do the same but using a digital twin created with the MAP twinning method, just set <code v-pre>twinning_method</code> to <code v-pre>'map'</code>.
A full example can be found in <code v-pre>example/code/replay_intervals_map.py</code>.</p>
</div>
<h2 id="event-handlers" tabindex="-1"><a class="header-anchor" href="#event-handlers"><span>Event handlers</span></a></h2>
<p>The possibility to alter &quot;offline&quot; the original <code v-pre>data</code> before calling <code v-pre>rbg.replay()</code> alone is not sufficient for testing, for
example, a specific bolus calculation strategy, as the meal/insulin inputs usually depend on the current glucose value
and other surrounding conditions which cannot be known before simulation.</p>
<p>In this context, the ReplayBG <code v-pre>rbg.replay()</code> method can be fed by a set of callable Python functions, hereafter
referred to as &quot;handlers&quot;, that will handle the real-time generation of specific events during the simulation.</p>
<p>As such, event handlers allow users to decide whether to use the meal/insulin inputs defined offline by the <code v-pre>data</code>
parameter of <code v-pre>rbg.replay()</code> or those generated online, during simulation, by custom algorithms.</p>
<h3 id="implemented-handlers-and-logic" tabindex="-1"><a class="header-anchor" href="#implemented-handlers-and-logic"><span>Implemented handlers and logic</span></a></h3>
<p>The following scheme defines the logic followed by ReplayBG to decide the input source to use during simulation. Yellow
boxes represent input parameters of <code v-pre>rbg.replay()</code>, green boxes represent the input data actually used during
simulation.</p>
<p><img src="https://i.ibb.co/J2Z8KSw/replaybg-input-source.jpg" alt="&quot;Input source&quot;" title="Input source"></p>
<p>As showed in the figure, five different handlers can be defined:</p>
<ul>
<li><code v-pre>meal_generator_handler</code>: a function that will replace the carbohydrates of <code v-pre>data.cho</code> with meal data generated according to a
custom user-defined policy when <code v-pre>cho_source='generated'</code>.</li>
<li><code v-pre>bolus_calculator_handler</code>: a function that will replace the insulin of <code v-pre>data.bolus</code> with insulin bolus data generated according to a
custom user-defined policy when <code v-pre>bolus_source='dss'</code>.</li>
<li><code v-pre>basal_handler</code>: a function that will replace the insulin of <code v-pre>data.basal</code> with basal insulin data generated according to a
custom user-defined policy when <code v-pre>basal_source='dss'</code>.</li>
<li><code v-pre>correction_boluses_handler</code>: a function that will add correction insulin boluses generated according to a
custom user-defined policy when <code v-pre>enable_correction_boluses=True</code>.</li>
<li><code v-pre>hypotreatments_handler</code>: a function that will add rescue carbs generated according to a
custom user-defined policy when <code v-pre>enable_hypotreatments=True</code>.</li>
</ul>
<p>Each handler must comply to mandatory input/output specifications described in details in the following subsections.</p>
<h3 id="meal-generators" tabindex="-1"><a class="header-anchor" href="#meal-generators"><span>Meal generators</span></a></h3>
<p>A meal generator handler must be a Python function with <strong>4 outputs and 11 inputs</strong> defined as:</p>
<div class="language-python line-numbers-mode" data-highlighter="prismjs" data-ext="py" data-title="py"><pre v-pre><code><span class="line"><span class="token keyword">def</span> <span class="token operator">&lt;</span>handler_name<span class="token operator">></span><span class="token punctuation">(</span></span>
<span class="line">        glucose<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        meal<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        meal_type<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        meal_announcement<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        hypotreatments<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        bolus<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        basal<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        time<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        time_index<span class="token punctuation">:</span> <span class="token builtin">int</span><span class="token punctuation">,</span></span>
<span class="line">        dss<span class="token punctuation">:</span> <span class="token builtin">object</span><span class="token punctuation">,</span></span>
<span class="line">        is_single_meal<span class="token punctuation">:</span> <span class="token builtin">bool</span></span>
<span class="line">        <span class="token punctuation">)</span> <span class="token operator">-</span><span class="token operator">></span> <span class="token builtin">tuple</span><span class="token punctuation">[</span><span class="token builtin">float</span><span class="token punctuation">,</span> <span class="token builtin">float</span><span class="token punctuation">,</span> <span class="token builtin">str</span><span class="token punctuation">,</span> <span class="token builtin">object</span><span class="token punctuation">]</span><span class="token punctuation">:</span></span>
<span class="line"></span></code></pre>
<div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h4 id="input-parameters-1" tabindex="-1"><a class="header-anchor" href="#input-parameters-1"><span>Input parameters</span></a></h4>
<ul>
<li><code v-pre>glucose</code>: An np.ndarray as long as <code v-pre>simulation_length</code> containing all the simulated glucose concentrations (mg/dl)
up to <code v-pre>time_index</code>. The values after <code v-pre>time_index</code> should be ignored by the user.</li>
<li><code v-pre>meal</code>: An np.ndarray as long as <code v-pre>simulation_length</code> containing all the meals (g) up to
<code v-pre>time_index</code>. The values after <code v-pre>time_index</code> should be ignored.</li>
<li><code v-pre>meal_type</code>: An np.ndarray as long as <code v-pre>simulation_length</code> containing strings that represent the type of each meal in
<code v-pre>meal_announcement</code>:
<ul>
<li>If blueprint is <code v-pre>single-meal</code>, labels can be:
<ul>
<li><code v-pre>M</code>: main meal</li>
<li><code v-pre>O</code>: other meal</li>
</ul>
</li>
<li>If blueprint is <code v-pre>multi-meal</code>, labels can be:
<ul>
<li><code v-pre>B</code>: breakfast</li>
<li><code v-pre>L</code>: lunch</li>
<li><code v-pre>D</code>: dinner</li>
<li><code v-pre>S</code>: snack</li>
<li><code v-pre>H</code>: hypotreatment
The values after <code v-pre>time_index</code> should be ignored.</li>
</ul>
</li>
</ul>
</li>
<li><code v-pre>meal_announcement</code>: An np.ndarray as long as <code v-pre>simulation_length</code> containing all the meal announcements (g) up to
<code v-pre>time_index</code>. The values after <code v-pre>time_index</code> should be ignored.</li>
<li><code v-pre>hypotreatments</code>: An np.ndarray as long as <code v-pre>simulation_length</code> containing all the hypotreatment intakes (g/min) up to
<code v-pre>time_index</code>. If the blueprint is single meal, <code v-pre>hypotreatments</code> will contain only the hypotreatments generated by this
function during the simulation. If the blueprint is multi-meal, hypotreatments will ALSO contain the hypotreatments
already present in the given <code v-pre>data</code> (if <code v-pre>cho_source='data'</code>) labeled as such. The values after <code v-pre>time_index</code> should be
ignored.</li>
<li><code v-pre>bolus</code>: An np.ndarray as long as <code v-pre>simulation_length</code> containing all the insulin boluses (U/min) up to <code v-pre>time_index</code>.
The values after <code v-pre>time_index</code> should be ignored.</li>
<li><code v-pre>basal</code>: An np.ndarray as long as <code v-pre>simulation_length</code> containing all the insulin basal (U/min) up to <code v-pre>time_index</code>.
The values after <code v-pre>time_index</code> should be ignored.</li>
<li><code v-pre>time</code>: An np.ndarray as long as <code v-pre>simulation_length</code> containing the time corresponding to the current step (hours) up
to <code v-pre>time_index</code>. The values after <code v-pre>time_index</code> should be ignored.</li>
<li><code v-pre>time_index</code>: The index corresponding to the previous simulation step of the replay simulation. This basically
represent the progress of the simulation.</li>
<li><code v-pre>dss</code>: An object of type <code v-pre>DSS</code>. Might contain parameters usable by the handler. More about <code v-pre>dss</code> is discussed below
in the <a href="#the-dss-parameter">The <code v-pre>dss</code> parameter</a> section.</li>
<li><code v-pre>is_single_meal</code>: A boolean flag indicating if the handler is being used by a single meal blueprint or not.</li>
</ul>
<h4 id="output-parameters" tabindex="-1"><a class="header-anchor" href="#output-parameters"><span>Output parameters</span></a></h4>
<ul>
<li><code v-pre>c</code>: A float that is the meal amount to have at the next simulation step in (g/min), i.e., <code v-pre>time[time_index+1]</code>.</li>
<li><code v-pre>ma</code>: A float that is the meal announcement (which can be different from <code v-pre>c</code> due to carb counting errors) to have at
the next simulation step in (g/min), i.e., <code v-pre>time[time_index+1]</code>.</li>
<li><code v-pre>type</code>: A string that is the type of the generated meal. Can be 'M' or 'O' if the blueprint is single meal,
'B' 'L' 'D' or 'S' otherwise.</li>
<li><code v-pre>dss</code>: An object of type <code v-pre>DSS</code>. Might contain parameters usable by the handler. More about <code v-pre>dss</code> is discussed below
in the <a href="#the-dss-parameter">The <code v-pre>dss</code> parameter</a> section.</li>
</ul>
<h4 id="default-handler" tabindex="-1"><a class="header-anchor" href="#default-handler"><span>Default handler</span></a></h4>
<p>The default bolus calculator handler (which is called when no custom handlers are provided by the
user and <code v-pre>bolus_source='dss'</code>) is defined in <code v-pre>py_replay_bg.dss.default_dss_handler</code> and implements a super
simple generator that is &quot;put a main meal of 50 g of CHO in the first instant and announce only 40g. If <code v-pre>is_single_meal=True</code>,
the meal type will be 'M', otherwise it will be a breakfast, 'B'&quot;:</p>
<div class="language-python line-numbers-mode" data-highlighter="prismjs" data-ext="py" data-title="py"><pre v-pre><code><span class="line"><span class="token keyword">def</span> <span class="token function">default_meal_generator_handler</span><span class="token punctuation">(</span></span>
<span class="line">        glucose<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        meal<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        meal_type<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        meal_announcement<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        hypotreatments<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        bolus<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        basal<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        time<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        time_index<span class="token punctuation">:</span> <span class="token builtin">int</span><span class="token punctuation">,</span></span>
<span class="line">        dss<span class="token punctuation">:</span> <span class="token builtin">object</span><span class="token punctuation">,</span></span>
<span class="line">        is_single_meal<span class="token punctuation">:</span> <span class="token builtin">bool</span></span>
<span class="line">        <span class="token punctuation">)</span> <span class="token operator">-</span><span class="token operator">></span> <span class="token builtin">tuple</span><span class="token punctuation">[</span><span class="token builtin">float</span><span class="token punctuation">,</span> <span class="token builtin">float</span><span class="token punctuation">,</span> <span class="token builtin">str</span><span class="token punctuation">,</span> <span class="token builtin">object</span><span class="token punctuation">]</span><span class="token punctuation">:</span></span>
<span class="line"></span>
<span class="line">    <span class="token comment"># Default output values</span></span>
<span class="line">    c <span class="token operator">=</span> <span class="token number">0</span></span>
<span class="line">    ma <span class="token operator">=</span> <span class="token number">0</span></span>
<span class="line">    m_type <span class="token operator">=</span> <span class="token string">''</span></span>
<span class="line"></span>
<span class="line">    <span class="token comment"># If this is the first time instant...</span></span>
<span class="line">    <span class="token keyword">if</span> time_index <span class="token operator">==</span> <span class="token number">0</span><span class="token punctuation">:</span></span>
<span class="line"></span>
<span class="line">        <span class="token comment"># ...generate a snack meal of 50 g and announce just 40 g</span></span>
<span class="line">        c <span class="token operator">=</span> <span class="token number">50</span></span>
<span class="line">        ma <span class="token operator">=</span> <span class="token number">40</span></span>
<span class="line"></span>
<span class="line">        <span class="token keyword">if</span> is_single_meal<span class="token punctuation">:</span></span>
<span class="line">            m_type <span class="token operator">=</span> <span class="token string">'M'</span></span>
<span class="line">        <span class="token keyword">else</span><span class="token punctuation">:</span></span>
<span class="line">            m_type <span class="token operator">=</span> <span class="token string">'B'</span></span>
<span class="line"></span>
<span class="line">    <span class="token keyword">return</span> c<span class="token punctuation">,</span> ma<span class="token punctuation">,</span> m_type<span class="token punctuation">,</span> dss</span>
<span class="line"></span></code></pre>
<div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h3 id="bolus-calculators" tabindex="-1"><a class="header-anchor" href="#bolus-calculators"><span>Bolus calculators</span></a></h3>
<p>A bolus calculator handler must be a Python function with <strong>2 outputs and 9 inputs</strong> defined as:</p>
<div class="language-python line-numbers-mode" data-highlighter="prismjs" data-ext="py" data-title="py"><pre v-pre><code><span class="line"><span class="token keyword">def</span> <span class="token operator">&lt;</span>handler_name<span class="token operator">></span><span class="token punctuation">(</span></span>
<span class="line">        glucose<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        meal_announcement<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        meal_type<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        hypotreatments<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        bolus<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        basal<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        time<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        time_index<span class="token punctuation">:</span> <span class="token builtin">int</span><span class="token punctuation">,</span></span>
<span class="line">        dss<span class="token punctuation">:</span> <span class="token builtin">object</span></span>
<span class="line">        <span class="token punctuation">)</span> <span class="token operator">-</span><span class="token operator">></span> <span class="token builtin">tuple</span><span class="token punctuation">[</span><span class="token builtin">float</span><span class="token punctuation">,</span> <span class="token builtin">object</span><span class="token punctuation">]</span><span class="token punctuation">:</span></span>
<span class="line"></span></code></pre>
<div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h4 id="input-parameters-2" tabindex="-1"><a class="header-anchor" href="#input-parameters-2"><span>Input parameters</span></a></h4>
<ul>
<li><code v-pre>glucose</code>: An np.ndarray as long as <code v-pre>simulation_length</code> containing all the simulated glucose concentrations (mg/dl)
up to <code v-pre>time_index</code>. The values after <code v-pre>time_index</code> should be ignored by the user.</li>
<li><code v-pre>meal_announcement</code>: An np.ndarray as long as <code v-pre>simulation_length</code> containing all the meal announcements (g) up to
<code v-pre>time_index</code>. The values after <code v-pre>time_index</code> should be ignored.</li>
<li><code v-pre>meal_type</code>: An np.ndarray as long as <code v-pre>simulation_length</code> containing strings that represent the type of each meal in
<code v-pre>meal_announcement</code>:
<ul>
<li>If blueprint is <code v-pre>single-meal</code>, labels can be:
<ul>
<li><code v-pre>M</code>: main meal</li>
<li><code v-pre>O</code>: other meal</li>
</ul>
</li>
<li>If blueprint is <code v-pre>multi-meal</code>, labels can be:
<ul>
<li><code v-pre>B</code>: breakfast</li>
<li><code v-pre>L</code>: lunch</li>
<li><code v-pre>D</code>: dinner</li>
<li><code v-pre>S</code>: snack</li>
<li><code v-pre>H</code>: hypotreatment
The values after <code v-pre>time_index</code> should be ignored.</li>
</ul>
</li>
</ul>
</li>
<li><code v-pre>hypotreatments</code>: An np.ndarray as long as <code v-pre>simulation_length</code> containing all the hypotreatment intakes (g/min) up to
<code v-pre>time_index</code>. If the blueprint is single meal, <code v-pre>hypotreatments</code> will contain only the hypotreatments generated by this
function during the simulation. If the blueprint is multi-meal, hypotreatments will ALSO contain the hypotreatments
already present in the given <code v-pre>data</code> (if <code v-pre>cho_source='data'</code>) labeled as such. The values after <code v-pre>time_index</code> should be
ignored.</li>
<li><code v-pre>bolus</code>: An np.ndarray as long as <code v-pre>simulation_length</code> containing all the insulin boluses (U/min) up to <code v-pre>time_index</code>.
The values after <code v-pre>time_index</code> should be ignored.</li>
<li><code v-pre>basal</code>: An np.ndarray as long as <code v-pre>simulation_length</code> containing all the insulin basal (U/min) up to <code v-pre>time_index</code>.
The values after <code v-pre>time_index</code> should be ignored.</li>
<li><code v-pre>time</code>: An np.ndarray as long as <code v-pre>simulation_length</code> containing the time corresponding to the current step (hours) up
to <code v-pre>time_index</code>. The values after <code v-pre>time_index</code> should be ignored.</li>
<li><code v-pre>time_index</code>: The index corresponding to the previous simulation step of the replay simulation. This basically
represent the progress of the simulation.</li>
<li><code v-pre>dss</code>: An object of type <code v-pre>DSS</code>. Might contain parameters usable by the handler. More about <code v-pre>dss</code> is discussed below
in the <a href="#the-dss-parameter">The <code v-pre>dss</code> parameter</a> section.</li>
</ul>
<h4 id="output-parameters-1" tabindex="-1"><a class="header-anchor" href="#output-parameters-1"><span>Output parameters</span></a></h4>
<ul>
<li><code v-pre>b</code>: A float that is the bolus insulin to administer at the next simulation step in (U/min), i.e., <code v-pre>time[time_index+1]</code>.</li>
<li><code v-pre>dss</code>: An object of type <code v-pre>DSS</code>. Might contain parameters usable by the handler. More about <code v-pre>dss</code> is discussed below
in the <a href="#the-dss-parameter">The <code v-pre>dss</code> parameter</a> section.</li>
</ul>
<h4 id="default-handler-1" tabindex="-1"><a class="header-anchor" href="#default-handler-1"><span>Default handler</span></a></h4>
<p>The default bolus calculator handler (which is called when no custom handlers are provided by the
user and <code v-pre>bolus_source='dss'</code>) is defined in <code v-pre>py_replay_bg.dss.default_dss_handler</code> and implements the standard
bolus calculator formula <mjx-container v-pre class="MathJax" jax="SVG" style="position: relative;"><svg style="vertical-align: -0.566ex;" xmlns="http://www.w3.org/2000/svg" width="40.812ex" height="2.262ex" role="img" focusable="false" viewBox="0 -750 18038.9 1000" aria-hidden="true"><g stroke="currentColor" fill="currentColor" stroke-width="0" transform="scale(1,-1)"><g data-mml-node="math"><g data-mml-node="mi"><path data-c="1D435" d="M231 637Q204 637 199 638T194 649Q194 676 205 682Q206 683 335 683Q594 683 608 681Q671 671 713 636T756 544Q756 480 698 429T565 360L555 357Q619 348 660 311T702 219Q702 146 630 78T453 1Q446 0 242 0Q42 0 39 2Q35 5 35 10Q35 17 37 24Q42 43 47 45Q51 46 62 46H68Q95 46 128 49Q142 52 147 61Q150 65 219 339T288 628Q288 635 231 637ZM649 544Q649 574 634 600T585 634Q578 636 493 637Q473 637 451 637T416 636H403Q388 635 384 626Q382 622 352 506Q352 503 351 500L320 374H401Q482 374 494 376Q554 386 601 434T649 544ZM595 229Q595 273 572 302T512 336Q506 337 429 337Q311 337 310 336Q310 334 293 263T258 122L240 52Q240 48 252 48T333 46Q422 46 429 47Q491 54 543 105T595 229Z"></path></g><g data-mml-node="mo" transform="translate(1036.8,0)"><path data-c="3D" d="M56 347Q56 360 70 367H707Q722 359 722 347Q722 336 708 328L390 327H72Q56 332 56 347ZM56 153Q56 168 72 173H708Q722 163 722 153Q722 140 707 133H70Q56 140 56 153Z"></path></g><g data-mml-node="mi" transform="translate(2092.6,0)"><path data-c="1D436" d="M50 252Q50 367 117 473T286 641T490 704Q580 704 633 653Q642 643 648 636T656 626L657 623Q660 623 684 649Q691 655 699 663T715 679T725 690L740 705H746Q760 705 760 698Q760 694 728 561Q692 422 692 421Q690 416 687 415T669 413H653Q647 419 647 422Q647 423 648 429T650 449T651 481Q651 552 619 605T510 659Q484 659 454 652T382 628T299 572T226 479Q194 422 175 346T156 222Q156 108 232 58Q280 24 350 24Q441 24 512 92T606 240Q610 253 612 255T628 257Q648 257 648 248Q648 243 647 239Q618 132 523 55T319 -22Q206 -22 128 53T50 252Z"></path></g><g data-mml-node="mi" transform="translate(2852.6,0)"><path data-c="1D43B" d="M228 637Q194 637 192 641Q191 643 191 649Q191 673 202 682Q204 683 219 683Q260 681 355 681Q389 681 418 681T463 682T483 682Q499 682 499 672Q499 670 497 658Q492 641 487 638H485Q483 638 480 638T473 638T464 637T455 637Q416 636 405 634T387 623Q384 619 355 500Q348 474 340 442T328 395L324 380Q324 378 469 378H614L615 381Q615 384 646 504Q674 619 674 627T617 637Q594 637 587 639T580 648Q580 650 582 660Q586 677 588 679T604 682Q609 682 646 681T740 680Q802 680 835 681T871 682Q888 682 888 672Q888 645 876 638H874Q872 638 869 638T862 638T853 637T844 637Q805 636 794 634T776 623Q773 618 704 340T634 58Q634 51 638 51Q646 48 692 46H723Q729 38 729 37T726 19Q722 6 716 0H701Q664 2 567 2Q533 2 504 2T458 2T437 1Q420 1 420 10Q420 15 423 24Q428 43 433 45Q437 46 448 46H454Q481 46 514 49Q520 50 522 50T528 55T534 64T540 82T547 110T558 153Q565 181 569 198Q602 330 602 331T457 332H312L279 197Q245 63 245 58Q245 51 253 49T303 46H334Q340 38 340 37T337 19Q333 6 327 0H312Q275 2 178 2Q144 2 115 2T69 2T48 1Q31 1 31 10Q31 12 34 24Q39 43 44 45Q48 46 59 46H65Q92 46 125 49Q139 52 144 61Q147 65 216 339T285 628Q285 635 228 637Z"></path></g><g data-mml-node="mi" transform="translate(3740.6,0)"><path data-c="1D442" d="M740 435Q740 320 676 213T511 42T304 -22Q207 -22 138 35T51 201Q50 209 50 244Q50 346 98 438T227 601Q351 704 476 704Q514 704 524 703Q621 689 680 617T740 435ZM637 476Q637 565 591 615T476 665Q396 665 322 605Q242 542 200 428T157 216Q157 126 200 73T314 19Q404 19 485 98T608 313Q637 408 637 476Z"></path></g><g data-mml-node="TeXAtom" data-mjx-texclass="ORD" transform="translate(4503.6,0)"><g data-mml-node="mo"><path data-c="2F" d="M423 750Q432 750 438 744T444 730Q444 725 271 248T92 -240Q85 -250 75 -250Q68 -250 62 -245T56 -231Q56 -221 230 257T407 740Q411 750 423 750Z"></path></g></g><g data-mml-node="mi" transform="translate(5003.6,0)"><path data-c="1D436" d="M50 252Q50 367 117 473T286 641T490 704Q580 704 633 653Q642 643 648 636T656 626L657 623Q660 623 684 649Q691 655 699 663T715 679T725 690L740 705H746Q760 705 760 698Q760 694 728 561Q692 422 692 421Q690 416 687 415T669 413H653Q647 419 647 422Q647 423 648 429T650 449T651 481Q651 552 619 605T510 659Q484 659 454 652T382 628T299 572T226 479Q194 422 175 346T156 222Q156 108 232 58Q280 24 350 24Q441 24 512 92T606 240Q610 253 612 255T628 257Q648 257 648 248Q648 243 647 239Q618 132 523 55T319 -22Q206 -22 128 53T50 252Z"></path></g><g data-mml-node="mi" transform="translate(5763.6,0)"><path data-c="1D445" d="M230 637Q203 637 198 638T193 649Q193 676 204 682Q206 683 378 683Q550 682 564 680Q620 672 658 652T712 606T733 563T739 529Q739 484 710 445T643 385T576 351T538 338L545 333Q612 295 612 223Q612 212 607 162T602 80V71Q602 53 603 43T614 25T640 16Q668 16 686 38T712 85Q717 99 720 102T735 105Q755 105 755 93Q755 75 731 36Q693 -21 641 -21H632Q571 -21 531 4T487 82Q487 109 502 166T517 239Q517 290 474 313Q459 320 449 321T378 323H309L277 193Q244 61 244 59Q244 55 245 54T252 50T269 48T302 46H333Q339 38 339 37T336 19Q332 6 326 0H311Q275 2 180 2Q146 2 117 2T71 2T50 1Q33 1 33 10Q33 12 36 24Q41 43 46 45Q50 46 61 46H67Q94 46 127 49Q141 52 146 61Q149 65 218 339T287 628Q287 635 230 637ZM630 554Q630 586 609 608T523 636Q521 636 500 636T462 637H440Q393 637 386 627Q385 624 352 494T319 361Q319 360 388 360Q466 361 492 367Q556 377 592 426Q608 449 619 486T630 554Z"></path></g><g data-mml-node="mo" transform="translate(6744.8,0)"><path data-c="2B" d="M56 237T56 250T70 270H369V420L370 570Q380 583 389 583Q402 583 409 568V270H707Q722 262 722 250T707 230H409V-68Q401 -82 391 -82H389H387Q375 -82 369 -68V230H70Q56 237 56 250Z"></path></g><g data-mml-node="mo" transform="translate(7745,0)"><path data-c="28" d="M94 250Q94 319 104 381T127 488T164 576T202 643T244 695T277 729T302 750H315H319Q333 750 333 741Q333 738 316 720T275 667T226 581T184 443T167 250T184 58T225 -81T274 -167T316 -220T333 -241Q333 -250 318 -250H315H302L274 -226Q180 -141 137 -14T94 250Z"></path></g><g data-mml-node="mi" transform="translate(8134,0)"><path data-c="1D43A" d="M50 252Q50 367 117 473T286 641T490 704Q580 704 633 653Q642 643 648 636T656 626L657 623Q660 623 684 649Q691 655 699 663T715 679T725 690L740 705H746Q760 705 760 698Q760 694 728 561Q692 422 692 421Q690 416 687 415T669 413H653Q647 419 647 422Q647 423 648 429T650 449T651 481Q651 552 619 605T510 659Q492 659 471 656T418 643T357 615T294 567T236 496T189 394T158 260Q156 242 156 221Q156 173 170 136T206 79T256 45T308 28T353 24Q407 24 452 47T514 106Q517 114 529 161T541 214Q541 222 528 224T468 227H431Q425 233 425 235T427 254Q431 267 437 273H454Q494 271 594 271Q634 271 659 271T695 272T707 272Q721 272 721 263Q721 261 719 249Q714 230 709 228Q706 227 694 227Q674 227 653 224Q646 221 643 215T629 164Q620 131 614 108Q589 6 586 3Q584 1 581 1Q571 1 553 21T530 52Q530 53 528 52T522 47Q448 -22 322 -22Q201 -22 126 55T50 252Z"></path></g><g data-mml-node="mi" transform="translate(8920,0)"><path data-c="1D436" d="M50 252Q50 367 117 473T286 641T490 704Q580 704 633 653Q642 643 648 636T656 626L657 623Q660 623 684 649Q691 655 699 663T715 679T725 690L740 705H746Q760 705 760 698Q760 694 728 561Q692 422 692 421Q690 416 687 415T669 413H653Q647 419 647 422Q647 423 648 429T650 449T651 481Q651 552 619 605T510 659Q484 659 454 652T382 628T299 572T226 479Q194 422 175 346T156 222Q156 108 232 58Q280 24 350 24Q441 24 512 92T606 240Q610 253 612 255T628 257Q648 257 648 248Q648 243 647 239Q618 132 523 55T319 -22Q206 -22 128 53T50 252Z"></path></g><g data-mml-node="mo" transform="translate(9902.2,0)"><path data-c="2212" d="M84 237T84 250T98 270H679Q694 262 694 250T679 230H98Q84 237 84 250Z"></path></g><g data-mml-node="mi" transform="translate(10902.4,0)"><path data-c="1D43A" d="M50 252Q50 367 117 473T286 641T490 704Q580 704 633 653Q642 643 648 636T656 626L657 623Q660 623 684 649Q691 655 699 663T715 679T725 690L740 705H746Q760 705 760 698Q760 694 728 561Q692 422 692 421Q690 416 687 415T669 413H653Q647 419 647 422Q647 423 648 429T650 449T651 481Q651 552 619 605T510 659Q492 659 471 656T418 643T357 615T294 567T236 496T189 394T158 260Q156 242 156 221Q156 173 170 136T206 79T256 45T308 28T353 24Q407 24 452 47T514 106Q517 114 529 161T541 214Q541 222 528 224T468 227H431Q425 233 425 235T427 254Q431 267 437 273H454Q494 271 594 271Q634 271 659 271T695 272T707 272Q721 272 721 263Q721 261 719 249Q714 230 709 228Q706 227 694 227Q674 227 653 224Q646 221 643 215T629 164Q620 131 614 108Q589 6 586 3Q584 1 581 1Q571 1 553 21T530 52Q530 53 528 52T522 47Q448 -22 322 -22Q201 -22 126 55T50 252Z"></path></g><g data-mml-node="mi" transform="translate(11688.4,0)"><path data-c="1D447" d="M40 437Q21 437 21 445Q21 450 37 501T71 602L88 651Q93 669 101 677H569H659Q691 677 697 676T704 667Q704 661 687 553T668 444Q668 437 649 437Q640 437 637 437T631 442L629 445Q629 451 635 490T641 551Q641 586 628 604T573 629Q568 630 515 631Q469 631 457 630T439 622Q438 621 368 343T298 60Q298 48 386 46Q418 46 427 45T436 36Q436 31 433 22Q429 4 424 1L422 0Q419 0 415 0Q410 0 363 1T228 2Q99 2 64 0H49Q43 6 43 9T45 27Q49 40 55 46H83H94Q174 46 189 55Q190 56 191 56Q196 59 201 76T241 233Q258 301 269 344Q339 619 339 625Q339 630 310 630H279Q212 630 191 624Q146 614 121 583T67 467Q60 445 57 441T43 437H40Z"></path></g><g data-mml-node="mo" transform="translate(12392.4,0)"><path data-c="29" d="M60 749L64 750Q69 750 74 750H86L114 726Q208 641 251 514T294 250Q294 182 284 119T261 12T224 -76T186 -143T145 -194T113 -227T90 -246Q87 -249 86 -250H74Q66 -250 63 -250T58 -247T55 -238Q56 -237 66 -225Q221 -64 221 250T66 725Q56 737 55 738Q55 746 60 749Z"></path></g><g data-mml-node="TeXAtom" data-mjx-texclass="ORD" transform="translate(12781.4,0)"><g data-mml-node="mo"><path data-c="2F" d="M423 750Q432 750 438 744T444 730Q444 725 271 248T92 -240Q85 -250 75 -250Q68 -250 62 -245T56 -231Q56 -221 230 257T407 740Q411 750 423 750Z"></path></g></g><g data-mml-node="mi" transform="translate(13281.4,0)"><path data-c="1D436" d="M50 252Q50 367 117 473T286 641T490 704Q580 704 633 653Q642 643 648 636T656 626L657 623Q660 623 684 649Q691 655 699 663T715 679T725 690L740 705H746Q760 705 760 698Q760 694 728 561Q692 422 692 421Q690 416 687 415T669 413H653Q647 419 647 422Q647 423 648 429T650 449T651 481Q651 552 619 605T510 659Q484 659 454 652T382 628T299 572T226 479Q194 422 175 346T156 222Q156 108 232 58Q280 24 350 24Q441 24 512 92T606 240Q610 253 612 255T628 257Q648 257 648 248Q648 243 647 239Q618 132 523 55T319 -22Q206 -22 128 53T50 252Z"></path></g><g data-mml-node="mi" transform="translate(14041.4,0)"><path data-c="1D439" d="M48 1Q31 1 31 11Q31 13 34 25Q38 41 42 43T65 46Q92 46 125 49Q139 52 144 61Q146 66 215 342T285 622Q285 629 281 629Q273 632 228 634H197Q191 640 191 642T193 659Q197 676 203 680H742Q749 676 749 669Q749 664 736 557T722 447Q720 440 702 440H690Q683 445 683 453Q683 454 686 477T689 530Q689 560 682 579T663 610T626 626T575 633T503 634H480Q398 633 393 631Q388 629 386 623Q385 622 352 492L320 363H375Q378 363 398 363T426 364T448 367T472 374T489 386Q502 398 511 419T524 457T529 475Q532 480 548 480H560Q567 475 567 470Q567 467 536 339T502 207Q500 200 482 200H470Q463 206 463 212Q463 215 468 234T473 274Q473 303 453 310T364 317H309L277 190Q245 66 245 60Q245 46 334 46H359Q365 40 365 39T363 19Q359 6 353 0H336Q295 2 185 2Q120 2 86 2T48 1Z"></path></g><g data-mml-node="mo" transform="translate(15012.7,0)"><path data-c="2212" d="M84 237T84 250T98 270H679Q694 262 694 250T679 230H98Q84 237 84 250Z"></path></g><g data-mml-node="mi" transform="translate(16012.9,0)"><path data-c="1D43C" d="M43 1Q26 1 26 10Q26 12 29 24Q34 43 39 45Q42 46 54 46H60Q120 46 136 53Q137 53 138 54Q143 56 149 77T198 273Q210 318 216 344Q286 624 286 626Q284 630 284 631Q274 637 213 637H193Q184 643 189 662Q193 677 195 680T209 683H213Q285 681 359 681Q481 681 487 683H497Q504 676 504 672T501 655T494 639Q491 637 471 637Q440 637 407 634Q393 631 388 623Q381 609 337 432Q326 385 315 341Q245 65 245 59Q245 52 255 50T307 46H339Q345 38 345 37T342 19Q338 6 332 0H316Q279 2 179 2Q143 2 113 2T65 2T43 1Z"></path></g><g data-mml-node="mi" transform="translate(16516.9,0)"><path data-c="1D442" d="M740 435Q740 320 676 213T511 42T304 -22Q207 -22 138 35T51 201Q50 209 50 244Q50 346 98 438T227 601Q351 704 476 704Q514 704 524 703Q621 689 680 617T740 435ZM637 476Q637 565 591 615T476 665Q396 665 322 605Q242 542 200 428T157 216Q157 126 200 73T314 19Q404 19 485 98T608 313Q637 408 637 476Z"></path></g><g data-mml-node="mi" transform="translate(17279.9,0)"><path data-c="1D435" d="M231 637Q204 637 199 638T194 649Q194 676 205 682Q206 683 335 683Q594 683 608 681Q671 671 713 636T756 544Q756 480 698 429T565 360L555 357Q619 348 660 311T702 219Q702 146 630 78T453 1Q446 0 242 0Q42 0 39 2Q35 5 35 10Q35 17 37 24Q42 43 47 45Q51 46 62 46H68Q95 46 128 49Q142 52 147 61Q150 65 219 339T288 628Q288 635 231 637ZM649 544Q649 574 634 600T585 634Q578 636 493 637Q473 637 451 637T416 636H403Q388 635 384 626Q382 622 352 506Q352 503 351 500L320 374H401Q482 374 494 376Q554 386 601 434T649 544ZM595 229Q595 273 572 302T512 336Q506 337 429 337Q311 337 310 336Q310 334 293 263T258 122L240 52Q240 48 252 48T333 46Q422 46 429 47Q491 54 543 105T595 229Z"></path></g></g></g></svg><mjx-assistive-mml unselectable="on" display="inline"><math xmlns="http://www.w3.org/1998/Math/MathML"><mi>B</mi><mo>=</mo><mi>C</mi><mi>H</mi><mi>O</mi><mrow data-mjx-texclass="ORD"><mo>/</mo></mrow><mi>C</mi><mi>R</mi><mo>+</mo><mo stretchy="false">(</mo><mi>G</mi><mi>C</mi><mo>−</mo><mi>G</mi><mi>T</mi><mo stretchy="false">)</mo><mrow data-mjx-texclass="ORD"><mo>/</mo></mrow><mi>C</mi><mi>F</mi><mo>−</mo><mi>I</mi><mi>O</mi><mi>B</mi></math></mjx-assistive-mml></mjx-container>:</p>
<div class="language-python line-numbers-mode" data-highlighter="prismjs" data-ext="py" data-title="py"><pre v-pre><code><span class="line"><span class="token keyword">def</span> <span class="token function">standard_bolus_calculator_handler</span><span class="token punctuation">(</span></span>
<span class="line">        glucose<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        meal_announcement<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        meal_type<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        hypotreatments<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        bolus<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        basal<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        time<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        time_index<span class="token punctuation">:</span> <span class="token builtin">int</span><span class="token punctuation">,</span></span>
<span class="line">        dss<span class="token punctuation">:</span> <span class="token builtin">object</span></span>
<span class="line">        <span class="token punctuation">)</span> <span class="token operator">-</span><span class="token operator">></span> <span class="token builtin">tuple</span><span class="token punctuation">[</span><span class="token builtin">float</span><span class="token punctuation">,</span> <span class="token builtin">object</span><span class="token punctuation">]</span><span class="token punctuation">:</span></span>
<span class="line"></span>
<span class="line">    b <span class="token operator">=</span> <span class="token number">0</span></span>
<span class="line"></span>
<span class="line">    <span class="token comment"># If a meal is announced...</span></span>
<span class="line">    <span class="token keyword">if</span> meal_announcement<span class="token punctuation">[</span>time_index<span class="token punctuation">]</span> <span class="token operator">></span> <span class="token number">0</span><span class="token punctuation">:</span></span>
<span class="line"></span>
<span class="line">        <span class="token comment"># compute iob</span></span>
<span class="line">        ts <span class="token operator">=</span> <span class="token number">5</span></span>
<span class="line"></span>
<span class="line">        k1 <span class="token operator">=</span> <span class="token number">0.0173</span></span>
<span class="line">        k2 <span class="token operator">=</span> <span class="token number">0.0116</span></span>
<span class="line">        k3 <span class="token operator">=</span> <span class="token number">6.73</span></span>
<span class="line"></span>
<span class="line">        iob_6h_curve <span class="token operator">=</span> np<span class="token punctuation">.</span>zeros<span class="token punctuation">(</span>shape<span class="token operator">=</span><span class="token punctuation">(</span><span class="token number">360</span><span class="token punctuation">,</span><span class="token punctuation">)</span><span class="token punctuation">)</span></span>
<span class="line"></span>
<span class="line">        <span class="token keyword">for</span> t <span class="token keyword">in</span> <span class="token builtin">range</span><span class="token punctuation">(</span><span class="token number">0</span><span class="token punctuation">,</span> <span class="token number">360</span><span class="token punctuation">)</span><span class="token punctuation">:</span></span>
<span class="line">            iob_6h_curve<span class="token punctuation">[</span>t<span class="token punctuation">]</span> <span class="token operator">=</span> <span class="token number">1</span> <span class="token operator">-</span> <span class="token number">0.75</span> <span class="token operator">*</span> <span class="token punctuation">(</span><span class="token punctuation">(</span><span class="token operator">-</span> k3 <span class="token operator">/</span> <span class="token punctuation">(</span>k2 <span class="token operator">*</span> <span class="token punctuation">(</span>k1 <span class="token operator">-</span> k2<span class="token punctuation">)</span><span class="token punctuation">)</span> <span class="token operator">*</span> <span class="token punctuation">(</span>np<span class="token punctuation">.</span>exp<span class="token punctuation">(</span><span class="token operator">-</span>k2 <span class="token operator">*</span> t <span class="token operator">/</span> <span class="token number">0.75</span><span class="token punctuation">)</span> <span class="token operator">-</span> <span class="token number">1</span><span class="token punctuation">)</span> <span class="token operator">+</span> k3 <span class="token operator">/</span> <span class="token punctuation">(</span></span>
<span class="line">                        k1 <span class="token operator">*</span> <span class="token punctuation">(</span>k1 <span class="token operator">-</span> k2<span class="token punctuation">)</span><span class="token punctuation">)</span> <span class="token operator">*</span> <span class="token punctuation">(</span>np<span class="token punctuation">.</span>exp<span class="token punctuation">(</span><span class="token operator">-</span>k1 <span class="token operator">*</span> t <span class="token operator">/</span> <span class="token number">0.75</span><span class="token punctuation">)</span> <span class="token operator">-</span> <span class="token number">1</span><span class="token punctuation">)</span><span class="token punctuation">)</span> <span class="token operator">/</span> <span class="token number">2.4947e4</span><span class="token punctuation">)</span></span>
<span class="line">        iob_6h_curve <span class="token operator">=</span> iob_6h_curve<span class="token punctuation">[</span>ts<span class="token punctuation">:</span><span class="token punctuation">:</span>ts<span class="token punctuation">]</span></span>
<span class="line"></span>
<span class="line">        iob <span class="token operator">=</span> np<span class="token punctuation">.</span>convolve<span class="token punctuation">(</span>bolus<span class="token punctuation">,</span> iob_6h_curve<span class="token punctuation">)</span></span>
<span class="line">        iob <span class="token operator">=</span> iob<span class="token punctuation">[</span>bolus<span class="token punctuation">.</span>shape<span class="token punctuation">[</span><span class="token number">0</span><span class="token punctuation">]</span> <span class="token operator">-</span> <span class="token number">1</span><span class="token punctuation">]</span></span>
<span class="line"></span>
<span class="line">        <span class="token comment"># get params</span></span>
<span class="line">        cr <span class="token operator">=</span> dss<span class="token punctuation">.</span>bolus_calculator_handler_params<span class="token punctuation">[</span><span class="token string">'cr'</span><span class="token punctuation">]</span> <span class="token keyword">if</span> <span class="token string">'cr'</span> <span class="token keyword">in</span> dss<span class="token punctuation">.</span>bolus_calculator_handler_params <span class="token keyword">else</span> <span class="token number">10</span></span>
<span class="line">        cf <span class="token operator">=</span> dss<span class="token punctuation">.</span>bolus_calculator_handler_params<span class="token punctuation">[</span><span class="token string">'cf'</span><span class="token punctuation">]</span> <span class="token keyword">if</span> <span class="token string">'cf'</span> <span class="token keyword">in</span> dss<span class="token punctuation">.</span>bolus_calculator_handler_params <span class="token keyword">else</span> <span class="token number">40</span></span>
<span class="line">        gt <span class="token operator">=</span> dss<span class="token punctuation">.</span>bolus_calculator_handler_params<span class="token punctuation">[</span><span class="token string">'gt'</span><span class="token punctuation">]</span> <span class="token keyword">if</span> <span class="token string">'gt'</span> <span class="token keyword">in</span> dss<span class="token punctuation">.</span>bolus_calculator_handler_params <span class="token keyword">else</span> <span class="token number">120</span></span>
<span class="line"></span>
<span class="line">        <span class="token comment"># ...give a bolus</span></span>
<span class="line">        b <span class="token operator">=</span> np<span class="token punctuation">.</span><span class="token builtin">max</span><span class="token punctuation">(</span><span class="token punctuation">[</span><span class="token number">0</span><span class="token punctuation">,</span> meal_announcement<span class="token punctuation">[</span>time_index<span class="token punctuation">]</span> <span class="token operator">/</span> cr <span class="token operator">+</span> <span class="token punctuation">(</span>glucose<span class="token punctuation">[</span>time_index<span class="token punctuation">]</span> <span class="token operator">-</span> gt<span class="token punctuation">)</span> <span class="token operator">/</span> cf <span class="token operator">-</span> iob<span class="token punctuation">]</span><span class="token punctuation">)</span></span>
<span class="line"></span>
<span class="line">    <span class="token keyword">return</span> b<span class="token punctuation">,</span> dss</span>
<span class="line"></span></code></pre>
<div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h3 id="basal-controllers" tabindex="-1"><a class="header-anchor" href="#basal-controllers"><span>Basal controllers</span></a></h3>
<p>A basal controller handler must be a Python function with <strong>2 outputs and 9 inputs</strong> defined as:</p>
<div class="language-python line-numbers-mode" data-highlighter="prismjs" data-ext="py" data-title="py"><pre v-pre><code><span class="line"><span class="token keyword">def</span> <span class="token operator">&lt;</span>handler_name<span class="token operator">></span><span class="token punctuation">(</span></span>
<span class="line">        glucose<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        meal_announcement<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        meal_type<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        hypotreatments<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        bolus<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        basal<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        time<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        time_index<span class="token punctuation">:</span> <span class="token builtin">int</span><span class="token punctuation">,</span></span>
<span class="line">        dss<span class="token punctuation">:</span> <span class="token builtin">object</span></span>
<span class="line">        <span class="token punctuation">)</span> <span class="token operator">-</span><span class="token operator">></span> <span class="token builtin">tuple</span><span class="token punctuation">[</span><span class="token builtin">float</span><span class="token punctuation">,</span> <span class="token builtin">object</span><span class="token punctuation">]</span><span class="token punctuation">:</span></span>
<span class="line"></span></code></pre>
<div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h4 id="input-parameters-3" tabindex="-1"><a class="header-anchor" href="#input-parameters-3"><span>Input parameters</span></a></h4>
<ul>
<li><code v-pre>glucose</code>: An np.ndarray as long as <code v-pre>simulation_length</code> containing all the simulated glucose concentrations (mg/dl)
up to <code v-pre>time_index</code>. The values after <code v-pre>time_index</code> should be ignored by the user.</li>
<li><code v-pre>meal_announcement</code>: An np.ndarray as long as <code v-pre>simulation_length</code> containing all the meal announcements (g) up to
<code v-pre>time_index</code>. The values after <code v-pre>time_index</code> should be ignored.</li>
<li><code v-pre>meal_type</code>: An np.ndarray as long as <code v-pre>simulation_length</code> containing strings that represent the type of each meal in
<code v-pre>meal_announcement</code>:
<ul>
<li>If blueprint is <code v-pre>single-meal</code>, labels can be:
<ul>
<li><code v-pre>M</code>: main meal</li>
<li><code v-pre>O</code>: other meal</li>
</ul>
</li>
<li>If blueprint is <code v-pre>multi-meal</code>, labels can be:
<ul>
<li><code v-pre>B</code>: breakfast</li>
<li><code v-pre>L</code>: lunch</li>
<li><code v-pre>D</code>: dinner</li>
<li><code v-pre>S</code>: snack</li>
<li><code v-pre>H</code>: hypotreatment
The values after <code v-pre>time_index</code> should be ignored.</li>
</ul>
</li>
</ul>
</li>
<li><code v-pre>hypotreatments</code>: An np.ndarray as long as <code v-pre>simulation_length</code> containing all the hypotreatment intakes (g/min) up to
<code v-pre>time_index</code>. If the blueprint is single meal, <code v-pre>hypotreatments</code> will contain only the hypotreatments generated by this
function during the simulation. If the blueprint is multi-meal, hypotreatments will ALSO contain the hypotreatments
already present in the given <code v-pre>data</code> (if <code v-pre>cho_source='data'</code>) labeled as such. The values after <code v-pre>time_index</code> should be
ignored.</li>
<li><code v-pre>bolus</code>: An np.ndarray as long as <code v-pre>simulation_length</code> containing all the insulin boluses (U/min) up to <code v-pre>time_index</code>.
The values after <code v-pre>time_index</code> should be ignored.</li>
<li><code v-pre>basal</code>: An np.ndarray as long as <code v-pre>simulation_length</code> containing all the insulin basal (U/min) up to <code v-pre>time_index</code>.
The values after <code v-pre>time_index</code> should be ignored.</li>
<li><code v-pre>time</code>: An np.ndarray as long as <code v-pre>simulation_length</code> containing the time corresponding to the current step (hours) up
to <code v-pre>time_index</code>. The values after <code v-pre>time_index</code> should be ignored.</li>
<li><code v-pre>time_index</code>: The index corresponding to the previous simulation step of the replay simulation. This basically
represent the progress of the simulation.</li>
<li><code v-pre>dss</code>: An object of type <code v-pre>DSS</code>. Might contain parameters usable by the handler. More about <code v-pre>dss</code> is discussed below
in the <a href="#the-dss-parameter">The <code v-pre>dss</code> parameter</a> section.</li>
</ul>
<h4 id="output-parameters-2" tabindex="-1"><a class="header-anchor" href="#output-parameters-2"><span>Output parameters</span></a></h4>
<ul>
<li><code v-pre>b</code>: A float that is the basal insulin to administer at the next simulation step in (U/min), i.e., <code v-pre>time[time_index+1]</code>.</li>
<li><code v-pre>dss</code>: An object of type <code v-pre>DSS</code>. Might contain parameters usable by the handler. More about <code v-pre>dss</code> is discussed below
in the <a href="#the-dss-parameter">The <code v-pre>dss</code> parameter</a> section.</li>
</ul>
<h4 id="default-handler-2" tabindex="-1"><a class="header-anchor" href="#default-handler-2"><span>Default handler</span></a></h4>
<p>The default basal controler handler (which is called when no custom handlers are provided by the
user and <code v-pre>basal_source='dss'</code>) is defined in <code v-pre>py_replay_bg.dss.default_dss_handler</code> and implements a naive algorithm, that is &quot;if
glucose &lt; 70, basal = 0; otherwise, basal = 0.01 U/min&quot;</p>
<div class="language-python line-numbers-mode" data-highlighter="prismjs" data-ext="py" data-title="py"><pre v-pre><code><span class="line"><span class="token keyword">def</span> <span class="token function">default_basal_handler</span><span class="token punctuation">(</span></span>
<span class="line">        glucose<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        meal_announcement<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        meal_type<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        hypotreatments<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        bolus<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        basal<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        time<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        time_index<span class="token punctuation">:</span> <span class="token builtin">int</span><span class="token punctuation">,</span></span>
<span class="line">        dss<span class="token punctuation">:</span> <span class="token builtin">object</span></span>
<span class="line">        <span class="token punctuation">)</span> <span class="token operator">-</span><span class="token operator">></span> <span class="token builtin">tuple</span><span class="token punctuation">[</span><span class="token builtin">float</span><span class="token punctuation">,</span> <span class="token builtin">object</span><span class="token punctuation">]</span><span class="token punctuation">:</span></span>
<span class="line"></span>
<span class="line">    b <span class="token operator">=</span> <span class="token number">0.01</span></span>
<span class="line"></span>
<span class="line">    <span class="token comment"># If G &lt; 70...</span></span>
<span class="line">    <span class="token keyword">if</span> glucose<span class="token punctuation">[</span>time_index<span class="token punctuation">]</span> <span class="token operator">&lt;</span> <span class="token number">70</span><span class="token punctuation">:</span></span>
<span class="line">        <span class="token comment"># ...set basal rate to 0</span></span>
<span class="line">        b <span class="token operator">=</span> <span class="token number">0</span></span>
<span class="line"></span>
<span class="line">    <span class="token keyword">return</span> b<span class="token punctuation">,</span> dss</span>
<span class="line"></span></code></pre>
<div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h3 id="corrective-insulin-bolus-generators" tabindex="-1"><a class="header-anchor" href="#corrective-insulin-bolus-generators"><span>Corrective insulin bolus generators</span></a></h3>
<p>A corrective insulin bolus generator handler must be a Python function with <strong>2 outputs and 9 inputs</strong> defined as:</p>
<div class="language-python line-numbers-mode" data-highlighter="prismjs" data-ext="py" data-title="py"><pre v-pre><code><span class="line"><span class="token keyword">def</span> <span class="token operator">&lt;</span>handler_name<span class="token operator">></span><span class="token punctuation">(</span></span>
<span class="line">        glucose<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        meal_announcement<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        meal_type<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        hypotreatments<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        bolus<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        basal<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        time<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        time_index<span class="token punctuation">:</span> <span class="token builtin">int</span><span class="token punctuation">,</span></span>
<span class="line">        dss<span class="token punctuation">:</span> <span class="token builtin">object</span></span>
<span class="line">        <span class="token punctuation">)</span> <span class="token operator">-</span><span class="token operator">></span> <span class="token builtin">tuple</span><span class="token punctuation">[</span><span class="token builtin">float</span><span class="token punctuation">,</span> <span class="token builtin">object</span><span class="token punctuation">]</span><span class="token punctuation">:</span></span>
<span class="line"></span></code></pre>
<div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h4 id="input-parameters-4" tabindex="-1"><a class="header-anchor" href="#input-parameters-4"><span>Input parameters</span></a></h4>
<ul>
<li><code v-pre>glucose</code>: An np.ndarray as long as <code v-pre>simulation_length</code> containing all the simulated glucose concentrations (mg/dl)
up to <code v-pre>time_index</code>. The values after <code v-pre>time_index</code> should be ignored by the user.</li>
<li><code v-pre>meal_announcement</code>: An np.ndarray as long as <code v-pre>simulation_length</code> containing all the meal announcements (g) up to
<code v-pre>time_index</code>. The values after <code v-pre>time_index</code> should be ignored.</li>
<li><code v-pre>meal_type</code>: An np.ndarray as long as <code v-pre>simulation_length</code> containing strings that represent the type of each meal in
<code v-pre>meal_announcement</code>:
<ul>
<li>If blueprint is <code v-pre>single-meal</code>, labels can be:
<ul>
<li><code v-pre>M</code>: main meal</li>
<li><code v-pre>O</code>: other meal</li>
</ul>
</li>
<li>If blueprint is <code v-pre>multi-meal</code>, labels can be:
<ul>
<li><code v-pre>B</code>: breakfast</li>
<li><code v-pre>L</code>: lunch</li>
<li><code v-pre>D</code>: dinner</li>
<li><code v-pre>S</code>: snack</li>
<li><code v-pre>H</code>: hypotreatment
The values after <code v-pre>time_index</code> should be ignored.</li>
</ul>
</li>
</ul>
</li>
<li><code v-pre>hypotreatments</code>: An np.ndarray as long as <code v-pre>simulation_length</code> containing all the hypotreatment intakes (g/min) up to
<code v-pre>time_index</code>. If the blueprint is single meal, <code v-pre>hypotreatments</code> will contain only the hypotreatments generated by this
function during the simulation. If the blueprint is multi-meal, hypotreatments will ALSO contain the hypotreatments
already present in the given <code v-pre>data</code> (if <code v-pre>cho_source='data'</code>) labeled as such. The values after <code v-pre>time_index</code> should be
ignored.</li>
<li><code v-pre>bolus</code>: An np.ndarray as long as <code v-pre>simulation_length</code> containing all the insulin boluses (U/min) up to <code v-pre>time_index</code>.
The values after <code v-pre>time_index</code> should be ignored.</li>
<li><code v-pre>basal</code>: An np.ndarray as long as <code v-pre>simulation_length</code> containing all the insulin basal (U/min) up to <code v-pre>time_index</code>.
The values after <code v-pre>time_index</code> should be ignored.</li>
<li><code v-pre>time</code>: An np.ndarray as long as <code v-pre>simulation_length</code> containing the time corresponding to the current step (hours) up
to <code v-pre>time_index</code>. The values after <code v-pre>time_index</code> should be ignored.</li>
<li><code v-pre>time_index</code>: The index corresponding to the previous simulation step of the replay simulation. This basically
represent the progress of the simulation.</li>
<li><code v-pre>dss</code>: An object of type <code v-pre>DSS</code>. Might contain parameters usable by the handler. More about <code v-pre>dss</code> is discussed below
in the <a href="#the-dss-parameter">The <code v-pre>dss</code> parameter</a> section.</li>
</ul>
<h4 id="output-parameters-3" tabindex="-1"><a class="header-anchor" href="#output-parameters-3"><span>Output parameters</span></a></h4>
<ul>
<li><code v-pre>cb</code>: A float that is the correction bolus to administer at the next simulation step in (U/min), i.e., <code v-pre>time[time_index+1]</code>.</li>
<li><code v-pre>dss</code>: An object of type <code v-pre>DSS</code>. Might contain parameters usable by the handler. More about <code v-pre>dss</code> is discussed below
in the <a href="#the-dss-parameter">The <code v-pre>dss</code> parameter</a> section.</li>
</ul>
<h4 id="default-handler-3" tabindex="-1"><a class="header-anchor" href="#default-handler-3"><span>Default handler</span></a></h4>
<p>The default corrective insulin bolus generator handler (which is called when no custom handlers are provided by the
user and <code v-pre>enable_correction_boluses=True</code>) is defined in <code v-pre>py_replay_bg.dss.default_dss_handler</code> and implements a naive algorithm, that is &quot;take a
correction bolus of 1 U every 1 hour while above 250 mg/dl&quot;</p>
<div class="language-python line-numbers-mode" data-highlighter="prismjs" data-ext="py" data-title="py"><pre v-pre><code><span class="line"><span class="token keyword">def</span> <span class="token function">corrects_above_250_handler</span><span class="token punctuation">(</span></span>
<span class="line">        glucose<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        meal_announcement<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        meal_type<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        hypotreatments<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        bolus<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        basal<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        time<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        time_index<span class="token punctuation">:</span> <span class="token builtin">int</span><span class="token punctuation">,</span></span>
<span class="line">        dss<span class="token punctuation">:</span> <span class="token builtin">object</span></span>
<span class="line">        <span class="token punctuation">)</span> <span class="token operator">-</span><span class="token operator">></span> <span class="token builtin">tuple</span><span class="token punctuation">[</span><span class="token builtin">float</span><span class="token punctuation">,</span> <span class="token builtin">object</span><span class="token punctuation">]</span><span class="token punctuation">:</span></span>
<span class="line"></span>
<span class="line">    cb <span class="token operator">=</span> <span class="token number">0</span></span>
<span class="line"></span>
<span class="line">    <span class="token comment"># If glucose is higher than 250...</span></span>
<span class="line">    <span class="token keyword">if</span> glucose<span class="token punctuation">[</span>time_index<span class="token punctuation">]</span> <span class="token operator">></span> <span class="token number">250</span><span class="token punctuation">:</span></span>
<span class="line"></span>
<span class="line">        <span class="token comment"># ...and if there are no boluses in the last 60 minutes, then take a CB</span></span>
<span class="line">        <span class="token keyword">if</span> time_index <span class="token operator">>=</span> <span class="token number">60</span> <span class="token keyword">and</span> <span class="token keyword">not</span> np<span class="token punctuation">.</span><span class="token builtin">any</span><span class="token punctuation">(</span>bolus<span class="token punctuation">[</span><span class="token punctuation">(</span>time_index <span class="token operator">-</span> <span class="token number">60</span><span class="token punctuation">)</span><span class="token punctuation">:</span>time_index<span class="token punctuation">]</span><span class="token punctuation">)</span><span class="token punctuation">:</span></span>
<span class="line">            cb <span class="token operator">=</span> <span class="token number">1</span></span>
<span class="line"></span>
<span class="line">    <span class="token keyword">return</span> cb<span class="token punctuation">,</span> dss</span>
<span class="line"></span></code></pre>
<div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h3 id="hypotreatment-generators" tabindex="-1"><a class="header-anchor" href="#hypotreatment-generators"><span>Hypotreatment generators</span></a></h3>
<p>A hypotreatment generator handler must be a Python function with <strong>2 outputs and 9 inputs</strong> defined as:</p>
<div class="language-python line-numbers-mode" data-highlighter="prismjs" data-ext="py" data-title="py"><pre v-pre><code><span class="line"><span class="token keyword">def</span> <span class="token operator">&lt;</span>handler_name<span class="token operator">></span><span class="token punctuation">(</span></span>
<span class="line">        glucose<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        meal_announcement<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        meal_type<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        hypotreatments<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        bolus<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        basal<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        time<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        time_index<span class="token punctuation">:</span> <span class="token builtin">int</span><span class="token punctuation">,</span></span>
<span class="line">        dss<span class="token punctuation">:</span> <span class="token builtin">object</span></span>
<span class="line">        <span class="token punctuation">)</span> <span class="token operator">-</span><span class="token operator">></span> <span class="token builtin">tuple</span><span class="token punctuation">[</span><span class="token builtin">float</span><span class="token punctuation">,</span> <span class="token builtin">object</span><span class="token punctuation">]</span><span class="token punctuation">:</span></span>
<span class="line"></span></code></pre>
<div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h4 id="input-parameters-5" tabindex="-1"><a class="header-anchor" href="#input-parameters-5"><span>Input parameters</span></a></h4>
<ul>
<li><code v-pre>glucose</code>: An np.ndarray as long as <code v-pre>simulation_length</code> containing all the simulated glucose concentrations (mg/dl)
up to <code v-pre>time_index</code>. The values after <code v-pre>time_index</code> should be ignored by the user.</li>
<li><code v-pre>meal_announcement</code>: An np.ndarray as long as <code v-pre>simulation_length</code> containing all the meal announcements (g) up to
<code v-pre>time_index</code>. The values after <code v-pre>time_index</code> should be ignored.</li>
<li><code v-pre>meal_type</code>: An np.ndarray as long as <code v-pre>simulation_length</code> containing strings that represent the type of each meal in
<code v-pre>meal_announcement</code>:
<ul>
<li>If blueprint is <code v-pre>single-meal</code>, labels can be:
<ul>
<li><code v-pre>M</code>: main meal</li>
<li><code v-pre>O</code>: other meal</li>
</ul>
</li>
<li>If blueprint is <code v-pre>multi-meal</code>, labels can be:
<ul>
<li><code v-pre>B</code>: breakfast</li>
<li><code v-pre>L</code>: lunch</li>
<li><code v-pre>D</code>: dinner</li>
<li><code v-pre>S</code>: snack</li>
<li><code v-pre>H</code>: hypotreatment
The values after <code v-pre>time_index</code> should be ignored.</li>
</ul>
</li>
</ul>
</li>
<li><code v-pre>hypotreatments</code>: An np.ndarray as long as <code v-pre>simulation_length</code> containing all the hypotreatment intakes (g/min) up to
<code v-pre>time_index</code>. If the blueprint is single meal, <code v-pre>hypotreatments</code> will contain only the hypotreatments generated by this
function during the simulation. If the blueprint is multi-meal, hypotreatments will ALSO contain the hypotreatments
already present in the given <code v-pre>data</code> (if <code v-pre>cho_source='data'</code>) labeled as such. The values after <code v-pre>time_index</code> should be
ignored.</li>
<li><code v-pre>bolus</code>: An np.ndarray as long as <code v-pre>simulation_length</code> containing all the insulin boluses (U/min) up to <code v-pre>time_index</code>.
The values after <code v-pre>time_index</code> should be ignored.</li>
<li><code v-pre>basal</code>: An np.ndarray as long as <code v-pre>simulation_length</code> containing all the insulin basal (U/min) up to <code v-pre>time_index</code>.
The values after <code v-pre>time_index</code> should be ignored.</li>
<li><code v-pre>time</code>: An np.ndarray as long as <code v-pre>simulation_length</code> containing the time corresponding to the current step (hours) up
to <code v-pre>time_index</code>. The values after <code v-pre>time_index</code> should be ignored.</li>
<li><code v-pre>time_index</code>: The index corresponding to the previous simulation step of the replay simulation. This basically
represent the progress of the simulation.</li>
<li><code v-pre>dss</code>: An object of type <code v-pre>DSS</code>. Might contain parameters usable by the handler. More about <code v-pre>dss</code> is discussed below
in the <a href="#the-dss-parameter">The <code v-pre>dss</code> parameter</a> section.</li>
</ul>
<h4 id="output-parameters-4" tabindex="-1"><a class="header-anchor" href="#output-parameters-4"><span>Output parameters</span></a></h4>
<ul>
<li><code v-pre>ht</code>: A float that is the hypotreatment to administer at the next simulation step in (g), i.e., <code v-pre>time[time_index+1]</code>.</li>
<li><code v-pre>dss</code>: An object of type <code v-pre>DSS</code>. Might contain parameters usable by the handler. More about <code v-pre>dss</code> is discussed below
in the <a href="#the-dss-parameter">The <code v-pre>dss</code> parameter</a> section.</li>
</ul>
<h4 id="default-handler-4" tabindex="-1"><a class="header-anchor" href="#default-handler-4"><span>Default handler</span></a></h4>
<p>The default hypotreatment generator handler (which is called when no custom handlers are provided by the
user and <code v-pre>enable_hypotreatments=True</code>) is defined in <code v-pre>py_replay_bg.dss.default_dss_handler</code> and implements the ADA
guidelines for hypotreatments generation that are &quot;&quot;take a hypotreatment of 10 g every 15 minutes while in
hypoglycemia&quot;</p>
<div class="language-python line-numbers-mode" data-highlighter="prismjs" data-ext="py" data-title="py"><pre v-pre><code><span class="line"><span class="token keyword">def</span> <span class="token function">ada_hypotreatments_handler</span><span class="token punctuation">(</span></span>
<span class="line">        glucose<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        meal_announcement<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        meal_type<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        hypotreatments<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        bolus<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        basal<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        time<span class="token punctuation">:</span> np<span class="token punctuation">.</span>ndarray<span class="token punctuation">,</span></span>
<span class="line">        time_index<span class="token punctuation">:</span> <span class="token builtin">int</span><span class="token punctuation">,</span></span>
<span class="line">        dss<span class="token punctuation">:</span> <span class="token builtin">object</span></span>
<span class="line">        <span class="token punctuation">)</span> <span class="token operator">-</span><span class="token operator">></span> <span class="token builtin">tuple</span><span class="token punctuation">[</span><span class="token builtin">float</span><span class="token punctuation">,</span> <span class="token builtin">object</span><span class="token punctuation">]</span><span class="token punctuation">:</span></span>
<span class="line"></span>
<span class="line">    ht <span class="token operator">=</span> <span class="token number">0</span></span>
<span class="line"></span>
<span class="line">    <span class="token comment"># If glucose is lower than 70...</span></span>
<span class="line">    <span class="token keyword">if</span> glucose<span class="token punctuation">[</span>time_index<span class="token punctuation">]</span> <span class="token operator">&lt;</span> <span class="token number">70</span><span class="token punctuation">:</span></span>
<span class="line"></span>
<span class="line">        <span class="token comment"># ...and if there are no CHO intakes in the last 15 minutes, then take an HT</span></span>
<span class="line">        <span class="token keyword">if</span> time_index <span class="token operator">>=</span> <span class="token number">15</span> <span class="token keyword">and</span> <span class="token keyword">not</span> np<span class="token punctuation">.</span><span class="token builtin">any</span><span class="token punctuation">(</span>hypotreatments<span class="token punctuation">[</span><span class="token punctuation">(</span>time_index <span class="token operator">-</span> <span class="token number">15</span><span class="token punctuation">)</span><span class="token punctuation">:</span>time_index<span class="token punctuation">]</span><span class="token punctuation">)</span><span class="token punctuation">:</span></span>
<span class="line">            ht <span class="token operator">=</span> <span class="token number">15</span></span>
<span class="line"></span>
<span class="line">    <span class="token keyword">return</span> ht<span class="token punctuation">,</span> dss</span>
<span class="line"></span></code></pre>
<div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h3 id="the-dss-parameter" tabindex="-1"><a class="header-anchor" href="#the-dss-parameter"><span>The <code v-pre>dss</code> parameter</span></a></h3>
<p><img src="https://i.ibb.co/LvzS371/replaybg-dss-variable.jpg" alt="&quot;dss variable flow&quot;" title="dss variable flow"></p>
<p>Each of the handler has the <code v-pre>dss</code> parameter as input/output.</p>
<p><code v-pre>dss</code> is an object of type <code v-pre>DSS</code>, created within the <code v-pre>rbg.replay()</code> method, that, as schematized in figure above,
has two main <strong>goals</strong>:</p>
<ol>
<li>it acts as a <strong>container</strong> of any hyperparameter and/or data one wants to pass to the custom handler functions.</li>
<li>it serves as <strong>memory area</strong></li>
</ol>
<p>Regarding the first point, the <code v-pre>dss</code> objects will contain the <code v-pre>correction_boluses_handler_params</code>,
<code v-pre>hypotreatments_handler_params</code>, <code v-pre>bolus_calculator_handler_params</code>, <code v-pre>basal_handler_params</code>, and <code v-pre>meal_generator_handler_params</code>
dictionaries given in input to <code v-pre>rbg.replay()</code>. As such, if one needs to pass specific parameters to the custom handler,
he/she should provide them in the dictionaries as subsequently access them as <code v-pre>dss.correction_boluses_handler_params</code>,
<code v-pre>dss.hypotreatments_handler_params</code>, <code v-pre>dss.bolus_calculator_handler_params</code>, <code v-pre>dss.basal_handler_params</code>,
and <code v-pre>dss.meal_generator_handler_params</code>, respectively.</p>
<p>Regarding the second point, being dictionaries mutable in Python, if needed it is possible to store values inside such
parameters of <code v-pre>dss</code> so that the handler will be able to access to them in the next call of the function.</p>
</div></template>


