<template><div><h1 id="get-started" tabindex="-1"><a class="header-anchor" href="#get-started"><span>Get started</span></a></h1>
<h2 id="installation" tabindex="-1"><a class="header-anchor" href="#installation"><span>Installation</span></a></h2>
<p><strong>ReplayBG</strong> can be installed via pypi by simply</p>
<div class="language-python line-numbers-mode" data-highlighter="prismjs" data-ext="py" data-title="py"><pre v-pre><code><span class="line">pip install py<span class="token operator">-</span>replay<span class="token operator">-</span>bg</span>
<span class="line"></span></code></pre>
<div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0"><div class="line-number"></div></div></div><h3 id="requirements" tabindex="-1"><a class="header-anchor" href="#requirements"><span>Requirements</span></a></h3>
<ul>
<li>Python &gt;= 3.11</li>
<li>List of python packages in <code v-pre>requirements.txt</code></li>
</ul>
<h2 id="preparation-imports-setup-and-data-loading" tabindex="-1"><a class="header-anchor" href="#preparation-imports-setup-and-data-loading"><span>Preparation: imports, setup, and data loading</span></a></h2>
<p>First of all import the core modules:</p>
<div class="language-python line-numbers-mode" data-highlighter="prismjs" data-ext="py" data-title="py"><pre v-pre><code><span class="line"><span class="token keyword">import</span> os</span>
<span class="line"><span class="token keyword">import</span> numpy <span class="token keyword">as</span> np</span>
<span class="line"><span class="token keyword">import</span> pandas <span class="token keyword">as</span> pd</span>
<span class="line"></span>
<span class="line"><span class="token keyword">from</span> multiprocessing <span class="token keyword">import</span> freeze_support</span>
<span class="line"></span></code></pre>
<div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>Here, <code v-pre>os</code> will be used to manage the filesystem, <code v-pre>numpy</code> and <code v-pre>pandas</code> to manipulate and manage the data to be used, and
<code v-pre>multiprocessing.freeze_support</code> to enable multiprocessing functionalities and run the twinning procedure in a faster,
parallelized way.</p>
<p>Then, we will import the necessary ReplayBG modules:</p>
<div class="language-python line-numbers-mode" data-highlighter="prismjs" data-ext="py" data-title="py"><pre v-pre><code><span class="line"><span class="token keyword">from</span> py_replay_bg<span class="token punctuation">.</span>py_replay_bg <span class="token keyword">import</span> ReplayBG</span>
<span class="line"><span class="token keyword">from</span> py_replay_bg<span class="token punctuation">.</span>visualizer <span class="token keyword">import</span> Visualizer</span>
<span class="line"><span class="token keyword">from</span> py_replay_bg<span class="token punctuation">.</span>analyzer <span class="token keyword">import</span> Analyzer</span>
<span class="line"></span></code></pre>
<div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>Here, <code v-pre>ReplayBG</code> is the core ReplayBG object, while <code v-pre>Analyzer</code> and <code v-pre>Visualizer</code> are utility objects that will be used to
respectively analyze and visualize the results that we will produce with ReplayBG.</p>
<p>Next steps consist of setting up some variables that will be used by ReplayBG environment.
First of all, we will run the twinning procedure in a parallelized way so let's start with:</p>
<div class="language-python line-numbers-mode" data-highlighter="prismjs" data-ext="py" data-title="py"><pre v-pre><code><span class="line"><span class="token keyword">if</span> __name__ <span class="token operator">==</span> <span class="token string">'__main__'</span><span class="token punctuation">:</span></span>
<span class="line">    freeze_support<span class="token punctuation">(</span><span class="token punctuation">)</span></span>
<span class="line"></span></code></pre>
<div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0"><div class="line-number"></div><div class="line-number"></div></div></div><p>Then, we will set the verbosity of ReplayBG:</p>
<div class="language-python line-numbers-mode" data-highlighter="prismjs" data-ext="py" data-title="py"><pre v-pre><code><span class="line">    verbose <span class="token operator">=</span> <span class="token boolean">True</span></span>
<span class="line"></span></code></pre>
<div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0"><div class="line-number"></div></div></div><p>This means that while we will run ReplayBG, we will see some informative messages to follow what the tool is doing.</p>
<div class="language-python line-numbers-mode" data-highlighter="prismjs" data-ext="py" data-title="py"><pre v-pre><code><span class="line">    plot_mode <span class="token operator">=</span> <span class="token boolean">False</span></span>
<span class="line"></span></code></pre>
<div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0"><div class="line-number"></div></div></div><p>This means that while we will run ReplayBG, plots will not be generated automatically.</p>
<p>Then, we need to decide what model to use for twinning the data at hand.</p>
<div class="language-python line-numbers-mode" data-highlighter="prismjs" data-ext="py" data-title="py"><pre v-pre><code><span class="line">    blueprint <span class="token operator">=</span> <span class="token string">'multi-meal'</span></span>
<span class="line">    save_folder <span class="token operator">=</span> os<span class="token punctuation">.</span>path<span class="token punctuation">.</span>join<span class="token punctuation">(</span>os<span class="token punctuation">.</span>path<span class="token punctuation">.</span>abspath<span class="token punctuation">(</span><span class="token string">''</span><span class="token punctuation">)</span><span class="token punctuation">,</span><span class="token string">'..'</span><span class="token punctuation">,</span><span class="token string">'..'</span><span class="token punctuation">,</span><span class="token string">'..'</span><span class="token punctuation">)</span></span>
<span class="line">    parallelize <span class="token operator">=</span> <span class="token boolean">True</span></span>
<span class="line"></span></code></pre>
<div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>Now, let's load some data to play with. In this example, we will use the data in <code v-pre>example/data/multi-meal_data.csv</code>
which contains a day data of a patient with T1D whose body weight is <code v-pre>100</code> kg:</p>
<div class="language-python line-numbers-mode" data-highlighter="prismjs" data-ext="py" data-title="py"><pre v-pre><code><span class="line">data <span class="token operator">=</span> pd<span class="token punctuation">.</span>read_csv<span class="token punctuation">(</span>os<span class="token punctuation">.</span>path<span class="token punctuation">.</span>join<span class="token punctuation">(</span>os<span class="token punctuation">.</span>path<span class="token punctuation">.</span>abspath<span class="token punctuation">(</span><span class="token string">''</span><span class="token punctuation">)</span><span class="token punctuation">,</span><span class="token string">'..'</span><span class="token punctuation">,</span> <span class="token string">'data'</span><span class="token punctuation">,</span> <span class="token string">'multi-meal_example.csv'</span><span class="token punctuation">)</span><span class="token punctuation">)</span></span>
<span class="line">data<span class="token punctuation">.</span>t <span class="token operator">=</span> pd<span class="token punctuation">.</span>to_datetime<span class="token punctuation">(</span>data<span class="token punctuation">[</span><span class="token string">'t'</span><span class="token punctuation">]</span><span class="token punctuation">)</span></span>
<span class="line"></span></code></pre>
<div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0"><div class="line-number"></div><div class="line-number"></div></div></div><p>Be careful, data in PyReplayBG must be provided in a <code v-pre>.csv.</code> file that must follow some strict requirements. For more info
on data requirements in <code v-pre>PyReplayBG</code> see the <a href="./data_requirements">Data Requirements</a>
section.</p>
<h2 id="step-1-identify-the-model-aka-fits-your-data" tabindex="-1"><a class="header-anchor" href="#step-1-identify-the-model-aka-fits-your-data"><span>Step 1. Identify the model (AKA fits your data)</span></a></h2>
<p>The first step of PyReplayBG consists of twinning its model (i.e., the digital twinning procedure). This can be done
with:</p>
<div class="language-python line-numbers-mode" data-highlighter="prismjs" data-ext="py" data-title="py"><pre v-pre><code><span class="line">modality <span class="token operator">=</span> <span class="token string">'identification'</span> <span class="token comment"># set modality as 'identification'</span></span>
<span class="line">bw <span class="token operator">=</span> <span class="token number">100</span> <span class="token comment"># set the patient body weight</span></span>
<span class="line">blueprint <span class="token operator">=</span> <span class="token string">'multi-meal'</span> <span class="token comment"># set the type of blueprint (can be single-meal or multi-meal)</span></span>
<span class="line">save_name <span class="token operator">=</span> <span class="token string">'test_multi_meal'</span> <span class="token comment"># set a save name</span></span>
<span class="line">n_steps <span class="token operator">=</span> <span class="token number">2500</span> <span class="token comment"># set the number of steps that will be used for identification (for multi-meal it should be at least 100k)</span></span>
<span class="line">save_folder <span class="token operator">=</span> os<span class="token punctuation">.</span>path<span class="token punctuation">.</span>abspath<span class="token punctuation">(</span><span class="token string">''</span><span class="token punctuation">)</span> <span class="token comment"># set the results folder to the current folder</span></span>
<span class="line"></span>
<span class="line"><span class="token comment"># Instantiate ReplayBG</span></span>
<span class="line">rbg <span class="token operator">=</span> ReplayBG<span class="token punctuation">(</span>modality<span class="token operator">=</span>modality<span class="token punctuation">,</span> data<span class="token operator">=</span>data<span class="token punctuation">,</span> bw<span class="token operator">=</span>bw<span class="token punctuation">,</span> blueprint<span class="token operator">=</span>blueprint<span class="token punctuation">,</span> save_name<span class="token operator">=</span>save_name<span class="token punctuation">,</span> save_folder<span class="token operator">=</span>save_folder<span class="token punctuation">,</span> n_steps<span class="token operator">=</span>n_steps<span class="token punctuation">)</span></span>
<span class="line"></span>
<span class="line"><span class="token comment"># Run it</span></span>
<span class="line">rbg<span class="token punctuation">.</span>run<span class="token punctuation">(</span>data<span class="token operator">=</span>data<span class="token punctuation">,</span> bw<span class="token operator">=</span>bw<span class="token punctuation">)</span></span>
<span class="line"></span></code></pre>
<div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>The above code, creates and runs an instance of PyReplayBG in <code v-pre>identification</code> modality, i.e., the necessary mode used
to run step 1.</p>
<p>Results of step 1 will be save in a <code v-pre>results</code> folder whose path is specified by the <code v-pre>save_folder</code> parameter.
Particularly, the <code v-pre>results</code> folder contains the following subfolders:</p>
<ul>
<li><code v-pre>draws</code>: contains the identified parameters.</li>
<li><code v-pre>mcmc_chains</code>: contains the raw chains of the Markov Chain Monte Carlo procedure if <code v-pre>save_chains</code> is <code v-pre>True</code> (by
default it is <code v-pre>False</code> since it would require a lot of storage)</li>
<li><code v-pre>workspaces</code>: contains the overall simulation results.</li>
</ul>
<p>At the hand of the procedure a plot will be produced (if <code v-pre>plot_mode</code> is <code v-pre>True</code>) showing the overall results.</p>
<div class="hint-container warning">
<p class="hint-container-title">Warning</p>
<p><code v-pre>save_name</code> is very important. It will uniquely identify the set of identified parameters for the given data. This means
that if one wants to run step 2 (see below) over those data, the same <code v-pre>save_name</code> must be used in both steps.</p>
</div>
<h2 id="step-2-replay" tabindex="-1"><a class="header-anchor" href="#step-2-replay"><span>Step 2. Replay</span></a></h2>
<p>Once identified, it is possible to start replay the data and test alternative insulin/cho therapies.</p>
<p>If one wants to simply replay the fitted data just run:</p>
<div class="language-python line-numbers-mode" data-highlighter="prismjs" data-ext="py" data-title="py"><pre v-pre><code><span class="line">modality <span class="token operator">=</span> <span class="token string">'replay'</span> <span class="token comment"># change modality as 'replay'</span></span>
<span class="line"></span>
<span class="line"><span class="token comment"># Instantiate ReplayBG</span></span>
<span class="line">rbg <span class="token operator">=</span> ReplayBG<span class="token punctuation">(</span>modality<span class="token operator">=</span>modality<span class="token punctuation">,</span> data<span class="token operator">=</span>data<span class="token punctuation">,</span> bw<span class="token operator">=</span>bw<span class="token punctuation">,</span> blueprint<span class="token operator">=</span>blueprint<span class="token punctuation">,</span> save_name<span class="token operator">=</span>save_name<span class="token punctuation">,</span> save_folder<span class="token operator">=</span>save_folder<span class="token punctuation">)</span></span>
<span class="line"></span>
<span class="line"><span class="token comment"># Run it</span></span>
<span class="line">rbg<span class="token punctuation">.</span>run<span class="token punctuation">(</span>data<span class="token operator">=</span>data<span class="token punctuation">,</span> bw<span class="token operator">=</span>bw<span class="token punctuation">)</span></span>
<span class="line"></span></code></pre>
<div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>Another example could be test &quot;waht happens if I reduce the bolus insulin by 30%?&quot;. To know the answer run:</p>
<div class="language-python line-numbers-mode" data-highlighter="prismjs" data-ext="py" data-title="py"><pre v-pre><code><span class="line">modality <span class="token operator">=</span> <span class="token string">'replay'</span> <span class="token comment"># change modality as 'replay'</span></span>
<span class="line"></span>
<span class="line"><span class="token comment"># Replay with less insulin</span></span>
<span class="line">data<span class="token punctuation">.</span>bolus <span class="token operator">=</span> data<span class="token punctuation">.</span>bolus <span class="token operator">*</span> <span class="token number">.7</span> <span class="token comment"># Reduce insulin boluses by 30%</span></span>
<span class="line"></span>
<span class="line"><span class="token comment"># Instantiate ReplayBG</span></span>
<span class="line">rbg <span class="token operator">=</span> ReplayBG<span class="token punctuation">(</span>modality<span class="token operator">=</span>modality<span class="token punctuation">,</span> data<span class="token operator">=</span>data<span class="token punctuation">,</span> bw<span class="token operator">=</span>bw<span class="token punctuation">,</span> blueprint<span class="token operator">=</span>blueprint<span class="token punctuation">,</span> save_name<span class="token operator">=</span>save_name<span class="token punctuation">,</span> save_folder<span class="token operator">=</span>save_folder<span class="token punctuation">)</span></span>
<span class="line"></span>
<span class="line"><span class="token comment"># Run it</span></span>
<span class="line">rbg<span class="token punctuation">.</span>run<span class="token punctuation">(</span>data<span class="token operator">=</span>data<span class="token punctuation">,</span> bw<span class="token operator">=</span>bw<span class="token punctuation">)</span></span>
<span class="line"></span></code></pre>
<div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="full-example" tabindex="-1"><a class="header-anchor" href="#full-example"><span>Full example</span></a></h2>
<p>A <code v-pre>.py</code> file with the full code of the quick start example can be found in <code v-pre>example/code/quick-start.py</code>.</p>
<div class="language-python line-numbers-mode" data-highlighter="prismjs" data-ext="py" data-title="py"><pre v-pre><code><span class="line"></span>
<span class="line"></span>
<span class="line"><span class="token keyword">if</span> __name__ <span class="token operator">==</span> <span class="token string">'__main__'</span><span class="token punctuation">:</span></span>
<span class="line">    freeze_support<span class="token punctuation">(</span><span class="token punctuation">)</span></span>
<span class="line"></span>
<span class="line">    <span class="token comment"># Set verbosity</span></span>
<span class="line">    verbose <span class="token operator">=</span> <span class="token boolean">True</span></span>
<span class="line">    plot_mode <span class="token operator">=</span> <span class="token boolean">False</span></span>
<span class="line"></span>
<span class="line">    <span class="token comment"># Set the number of steps for MCMC</span></span>
<span class="line">    n_steps <span class="token operator">=</span> <span class="token number">5000</span>  <span class="token comment"># 5k is for testing. In production, this should be >= 50k</span></span>
<span class="line"></span>
<span class="line">    <span class="token comment"># Set other parameters for twinning</span></span>
<span class="line">    blueprint <span class="token operator">=</span> <span class="token string">'multi-meal'</span></span>
<span class="line">    save_folder <span class="token operator">=</span> os<span class="token punctuation">.</span>path<span class="token punctuation">.</span>join<span class="token punctuation">(</span>os<span class="token punctuation">.</span>path<span class="token punctuation">.</span>abspath<span class="token punctuation">(</span><span class="token string">''</span><span class="token punctuation">)</span><span class="token punctuation">,</span><span class="token string">'..'</span><span class="token punctuation">,</span><span class="token string">'..'</span><span class="token punctuation">,</span><span class="token string">'..'</span><span class="token punctuation">)</span></span>
<span class="line">    parallelize <span class="token operator">=</span> <span class="token boolean">True</span></span>
<span class="line"></span>
<span class="line">    <span class="token comment"># load patient_info</span></span>
<span class="line">    patient_info <span class="token operator">=</span> pd<span class="token punctuation">.</span>read_csv<span class="token punctuation">(</span>os<span class="token punctuation">.</span>path<span class="token punctuation">.</span>join<span class="token punctuation">(</span>os<span class="token punctuation">.</span>path<span class="token punctuation">.</span>abspath<span class="token punctuation">(</span><span class="token string">''</span><span class="token punctuation">)</span><span class="token punctuation">,</span> <span class="token string">'..'</span><span class="token punctuation">,</span> <span class="token string">'data'</span><span class="token punctuation">,</span> <span class="token string">'patient_info.csv'</span><span class="token punctuation">)</span><span class="token punctuation">)</span></span>
<span class="line">    p <span class="token operator">=</span> np<span class="token punctuation">.</span>where<span class="token punctuation">(</span>patient_info<span class="token punctuation">[</span><span class="token string">'patient'</span><span class="token punctuation">]</span> <span class="token operator">==</span> <span class="token number">1</span><span class="token punctuation">)</span><span class="token punctuation">[</span><span class="token number">0</span><span class="token punctuation">]</span><span class="token punctuation">[</span><span class="token number">0</span><span class="token punctuation">]</span></span>
<span class="line">    <span class="token comment"># Set bw and u2ss</span></span>
<span class="line">    bw <span class="token operator">=</span> <span class="token builtin">float</span><span class="token punctuation">(</span>patient_info<span class="token punctuation">.</span>bw<span class="token punctuation">.</span>values<span class="token punctuation">[</span>p<span class="token punctuation">]</span><span class="token punctuation">)</span></span>
<span class="line">    u2ss <span class="token operator">=</span> <span class="token builtin">float</span><span class="token punctuation">(</span>patient_info<span class="token punctuation">.</span>u2ss<span class="token punctuation">.</span>values<span class="token punctuation">[</span>p<span class="token punctuation">]</span><span class="token punctuation">)</span></span>
<span class="line"></span>
<span class="line">    <span class="token comment"># Instantiate ReplayBG</span></span>
<span class="line">    rbg <span class="token operator">=</span> ReplayBG<span class="token punctuation">(</span>blueprint<span class="token operator">=</span>blueprint<span class="token punctuation">,</span> save_folder<span class="token operator">=</span>save_folder<span class="token punctuation">,</span></span>
<span class="line">                   yts<span class="token operator">=</span><span class="token number">5</span><span class="token punctuation">,</span> exercise<span class="token operator">=</span><span class="token boolean">False</span><span class="token punctuation">,</span></span>
<span class="line">                   seed<span class="token operator">=</span><span class="token number">1</span><span class="token punctuation">,</span></span>
<span class="line">                   verbose<span class="token operator">=</span>verbose<span class="token punctuation">,</span> plot_mode<span class="token operator">=</span>plot_mode<span class="token punctuation">)</span></span>
<span class="line"></span>
<span class="line">    <span class="token comment"># Load data and set save_name</span></span>
<span class="line">    data <span class="token operator">=</span> pd<span class="token punctuation">.</span>read_csv<span class="token punctuation">(</span>os<span class="token punctuation">.</span>path<span class="token punctuation">.</span>join<span class="token punctuation">(</span>os<span class="token punctuation">.</span>path<span class="token punctuation">.</span>abspath<span class="token punctuation">(</span><span class="token string">''</span><span class="token punctuation">)</span><span class="token punctuation">,</span> <span class="token string">'..'</span><span class="token punctuation">,</span> <span class="token string">'data'</span><span class="token punctuation">,</span> <span class="token string">'data_day_1.csv'</span><span class="token punctuation">)</span><span class="token punctuation">)</span></span>
<span class="line">    data<span class="token punctuation">.</span>t <span class="token operator">=</span> pd<span class="token punctuation">.</span>to_datetime<span class="token punctuation">(</span>data<span class="token punctuation">[</span><span class="token string">'t'</span><span class="token punctuation">]</span><span class="token punctuation">)</span></span>
<span class="line">    save_name <span class="token operator">=</span> <span class="token string">'data_day_1'</span></span>
<span class="line"></span>
<span class="line">    <span class="token keyword">print</span><span class="token punctuation">(</span><span class="token string">"Twinning "</span> <span class="token operator">+</span> save_name<span class="token punctuation">)</span></span>
<span class="line"></span>
<span class="line">    <span class="token comment"># Step 1. Run twinning procedure</span></span>
<span class="line">    rbg<span class="token punctuation">.</span>twin<span class="token punctuation">(</span>data<span class="token operator">=</span>data<span class="token punctuation">,</span> bw<span class="token operator">=</span>bw<span class="token punctuation">,</span> save_name<span class="token operator">=</span>save_name<span class="token punctuation">,</span></span>
<span class="line">             twinning_method<span class="token operator">=</span><span class="token string">'mcmc'</span><span class="token punctuation">,</span></span>
<span class="line">             parallelize<span class="token operator">=</span>parallelize<span class="token punctuation">,</span></span>
<span class="line">             n_steps<span class="token operator">=</span>n_steps<span class="token punctuation">,</span></span>
<span class="line">             u2ss<span class="token operator">=</span>u2ss<span class="token punctuation">)</span></span>
<span class="line"></span>
<span class="line">    <span class="token comment"># Step 2a. Replay the twin with the same input data to get the initial conditions for the subsequent day</span></span>
<span class="line">    replay_results <span class="token operator">=</span> rbg<span class="token punctuation">.</span>replay<span class="token punctuation">(</span>data<span class="token operator">=</span>data<span class="token punctuation">,</span> bw<span class="token operator">=</span>bw<span class="token punctuation">,</span> save_name<span class="token operator">=</span>save_name<span class="token punctuation">,</span></span>
<span class="line">                                twinning_method<span class="token operator">=</span><span class="token string">'mcmc'</span><span class="token punctuation">,</span></span>
<span class="line">                                save_workspace<span class="token operator">=</span><span class="token boolean">True</span><span class="token punctuation">,</span></span>
<span class="line">                                u2ss<span class="token operator">=</span>u2ss<span class="token punctuation">,</span></span>
<span class="line">                                save_suffix<span class="token operator">=</span><span class="token string">'_step_2a'</span><span class="token punctuation">)</span></span>
<span class="line"></span>
<span class="line">    <span class="token comment"># Visualize results and compare with the original glucose data</span></span>
<span class="line">    Visualizer<span class="token punctuation">.</span>plot_replay_results<span class="token punctuation">(</span>replay_results<span class="token punctuation">,</span> data<span class="token operator">=</span>data<span class="token punctuation">)</span></span>
<span class="line">    <span class="token comment"># Analyze results</span></span>
<span class="line">    analysis <span class="token operator">=</span> Analyzer<span class="token punctuation">.</span>analyze_replay_results<span class="token punctuation">(</span>replay_results<span class="token punctuation">,</span> data<span class="token operator">=</span>data<span class="token punctuation">)</span></span>
<span class="line">    <span class="token comment"># Print, for example, the fit MARD and the average glucose</span></span>
<span class="line">    <span class="token keyword">print</span><span class="token punctuation">(</span><span class="token string">'Fit MARD: %.2f %%'</span> <span class="token operator">%</span> analysis<span class="token punctuation">[</span><span class="token string">'median'</span><span class="token punctuation">]</span><span class="token punctuation">[</span><span class="token string">'twin'</span><span class="token punctuation">]</span><span class="token punctuation">[</span><span class="token string">'mard'</span><span class="token punctuation">]</span><span class="token punctuation">)</span></span>
<span class="line">    <span class="token keyword">print</span><span class="token punctuation">(</span><span class="token string">'Mean glucose: %.2f mg/dl'</span> <span class="token operator">%</span> analysis<span class="token punctuation">[</span><span class="token string">'median'</span><span class="token punctuation">]</span><span class="token punctuation">[</span><span class="token string">'glucose'</span><span class="token punctuation">]</span><span class="token punctuation">[</span><span class="token string">'variability'</span><span class="token punctuation">]</span><span class="token punctuation">[</span><span class="token string">'mean_glucose'</span><span class="token punctuation">]</span><span class="token punctuation">)</span></span>
<span class="line"></span>
<span class="line">    <span class="token comment"># Step 2b. Replay the twin with different input data (-30% bolus insulin) to experiment how glucose changes</span></span>
<span class="line">    data<span class="token punctuation">.</span>bolus <span class="token operator">=</span> data<span class="token punctuation">.</span>bolus <span class="token operator">*</span> <span class="token number">.7</span></span>
<span class="line">    replay_results <span class="token operator">=</span> rbg<span class="token punctuation">.</span>replay<span class="token punctuation">(</span>data<span class="token operator">=</span>data<span class="token punctuation">,</span> bw<span class="token operator">=</span>bw<span class="token punctuation">,</span> save_name<span class="token operator">=</span>save_name<span class="token punctuation">,</span></span>
<span class="line">                                twinning_method<span class="token operator">=</span><span class="token string">'mcmc'</span><span class="token punctuation">,</span></span>
<span class="line">                                save_workspace<span class="token operator">=</span><span class="token boolean">True</span><span class="token punctuation">,</span></span>
<span class="line">                                u2ss<span class="token operator">=</span>u2ss<span class="token punctuation">,</span></span>
<span class="line">                                save_suffix<span class="token operator">=</span><span class="token string">'_step_2b'</span><span class="token punctuation">)</span></span>
<span class="line"></span>
<span class="line">    <span class="token comment"># Visualize results</span></span>
<span class="line">    Visualizer<span class="token punctuation">.</span>plot_replay_results<span class="token punctuation">(</span>replay_results<span class="token punctuation">)</span></span>
<span class="line">    <span class="token comment"># Analyze results</span></span>
<span class="line">    analysis <span class="token operator">=</span> Analyzer<span class="token punctuation">.</span>analyze_replay_results<span class="token punctuation">(</span>replay_results<span class="token punctuation">)</span></span>
<span class="line"></span>
<span class="line">    <span class="token comment"># Print, for example, the average glucose</span></span>
<span class="line">    <span class="token keyword">print</span><span class="token punctuation">(</span><span class="token string">'Mean glucose: %.2f mg/dl'</span> <span class="token operator">%</span> analysis<span class="token punctuation">[</span><span class="token string">'median'</span><span class="token punctuation">]</span><span class="token punctuation">[</span><span class="token string">'glucose'</span><span class="token punctuation">]</span><span class="token punctuation">[</span><span class="token string">'variability'</span><span class="token punctuation">]</span><span class="token punctuation">[</span><span class="token string">'mean_glucose'</span><span class="token punctuation">]</span><span class="token punctuation">)</span></span>
<span class="line"></span>
<span class="line"></span></code></pre>
<div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div></div></template>


