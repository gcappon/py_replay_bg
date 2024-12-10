<template><div><h1 id="the-replaybg-object" tabindex="-1"><a class="header-anchor" href="#the-replaybg-object"><span>The ReplayBG Object</span></a></h1>
<p>The <code v-pre>ReplayBG</code> object is the core, key, object to instatiate when starting to work with the ReplayBG framework.</p>
<p>Its constructor is formally defined as:</p>
<div class="language-python line-numbers-mode" data-highlighter="prismjs" data-ext="py" data-title="py"><pre v-pre><code><span class="line"><span class="token keyword">from</span> py_replay_bg<span class="token punctuation">.</span>py_replay_bg <span class="token keyword">import</span> ReplayBG</span>
<span class="line"></span>
<span class="line">ReplayBG<span class="token punctuation">(</span>save_folder<span class="token punctuation">:</span> <span class="token builtin">str</span><span class="token punctuation">,</span> blueprint<span class="token punctuation">:</span> <span class="token builtin">str</span> <span class="token operator">=</span> <span class="token string">'single_meal'</span><span class="token punctuation">,</span></span>
<span class="line">    yts<span class="token punctuation">:</span> <span class="token builtin">int</span> <span class="token operator">=</span> <span class="token number">5</span><span class="token punctuation">,</span> exercise<span class="token punctuation">:</span> <span class="token builtin">bool</span> <span class="token operator">=</span> <span class="token boolean">False</span><span class="token punctuation">,</span></span>
<span class="line">    seed<span class="token punctuation">:</span> <span class="token builtin">int</span> <span class="token operator">=</span> <span class="token number">1</span><span class="token punctuation">,</span></span>
<span class="line">    plot_mode<span class="token punctuation">:</span> <span class="token builtin">bool</span> <span class="token operator">=</span> <span class="token boolean">True</span><span class="token punctuation">,</span> verbose<span class="token punctuation">:</span> <span class="token builtin">bool</span> <span class="token operator">=</span> <span class="token boolean">True</span><span class="token punctuation">)</span></span>
<span class="line"></span></code></pre>
<div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="input-parameters" tabindex="-1"><a class="header-anchor" href="#input-parameters"><span>Input parameters</span></a></h2>
<p>Let's inspect and describe each input parameter.</p>
<ul>
<li><code v-pre>save_folder</code>: a string defining the folder that will contain the results of the twinning procedure and the replay
simulations. This parameter is mandatory. More information on how to set it can be found in
<RouteLink to="/documentation/results_folder.html">The <em>results/</em> Folder</RouteLink> page.</li>
<li><code v-pre>blueprint</code>, optional, <code v-pre>{'single-meal', 'multi-meal'}</code>, default: <code v-pre>'single-meal'</code>: a string that specifies the blueprint to be used to create
the digital twin. More information on how to set it can be found in <RouteLink to="/documentation/choosing_blueprint.html">Choosing Blueprint</RouteLink> page.</li>
<li><code v-pre>yts</code>, optional, default: <code v-pre>5</code> : an integer that specifies the data sample time (in minutes).</li>
<li><code v-pre>exercise</code>, optional, default: <code v-pre>False</code>: a boolean that specifies whether to simulate exercise or not.</li>
<li><code v-pre>seed</code>, optional, default: <code v-pre>1</code>: an integer that specifies the random seed. For reproducibility.</li>
<li><code v-pre>plot_mode</code>, optional, default: <code v-pre>True</code>: a boolean that specifies whether to show the plot of the results or not. More
information on how to visualize the results of ReplayBG can be found in
<RouteLink to="/documentation/visualizing_replay_results.html">Visualizing Replay Results</RouteLink> page.</li>
<li><code v-pre>verbose</code>, optional, default: <code v-pre>True</code>: a boolean that specifies the verbosity of ReplayBG.</li>
</ul>
</div></template>


