<template><div><h1 id="the-results-folder" tabindex="-1"><a class="header-anchor" href="#the-results-folder"><span>The <em>results/</em> Folder</span></a></h1>
<p>All results of ReplayBG, i.e., both model parameters obtained via twinning procedure and replayed
glucose traces of a given scenario, will be saved in a folder named <code v-pre>results/</code>.</p>
<h2 id="choosing-the-path-of-results" tabindex="-1"><a class="header-anchor" href="#choosing-the-path-of-results"><span>Choosing the path of <em>results/</em></span></a></h2>
<p>When creating the ReplayBG object, user must decide the location of <code v-pre>results/</code>.
To do that, specify a custom location, relative to current <code v-pre>&lt;WORKING_DIRECTORY&gt;</code>
using the <code v-pre>save_folder</code> parameter of the <code v-pre>ReplayBG</code> object builder. For example,
to put <code v-pre>results/</code> in <code v-pre>&lt;WORKING_DIRECTORY&gt;/custom/path/location/</code>, simply:</p>
<div class="language-python line-numbers-mode" data-highlighter="prismjs" data-ext="py" data-title="py"><pre v-pre><code><span class="line">rbg <span class="token operator">=</span> ReplayBG<span class="token punctuation">(</span>save_folder<span class="token operator">=</span>os<span class="token punctuation">.</span>path<span class="token punctuation">.</span>join<span class="token punctuation">(</span><span class="token string">'custom'</span><span class="token punctuation">,</span> <span class="token string">'path'</span><span class="token punctuation">,</span> <span class="token string">'location'</span><span class="token punctuation">)</span><span class="token punctuation">,</span> <span class="token punctuation">.</span><span class="token punctuation">.</span><span class="token punctuation">.</span><span class="token punctuation">)</span></span>
<span class="line"></span></code></pre>
<div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0"><div class="line-number"></div></div></div><p>This means that if the user wants to put <code v-pre>results/</code> just in <code v-pre>&lt;WORKING_DIRECTORY&gt;</code>
he/she must use:</p>
<div class="language-python line-numbers-mode" data-highlighter="prismjs" data-ext="py" data-title="py"><pre v-pre><code><span class="line">rbg <span class="token operator">=</span> ReplayBG<span class="token punctuation">(</span>save_folder<span class="token operator">=</span>os<span class="token punctuation">.</span>path<span class="token punctuation">.</span>join<span class="token punctuation">(</span><span class="token string">''</span><span class="token punctuation">)</span><span class="token punctuation">,</span> <span class="token punctuation">.</span><span class="token punctuation">.</span><span class="token punctuation">.</span><span class="token punctuation">)</span></span>
<span class="line"></span></code></pre>
<div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0"><div class="line-number"></div></div></div><h2 id="what-s-inside" tabindex="-1"><a class="header-anchor" href="#what-s-inside"><span>What's inside</span></a></h2>
<p>The <code v-pre>results/</code> folder is organized as follows:</p>
<div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre v-pre><code><span class="line">results/</span>
<span class="line">|--- mcmc/</span>
<span class="line">|--- map/</span>
<span class="line">|--- workspaces/</span>
<span class="line"></span></code></pre>
<div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>where the <code v-pre>mcmc/</code> and <code v-pre>map/</code> subfolders contains the model parameters obtained via
MCMC-based and MAP-based twinning procedures, respectively; and the <code v-pre>workspaces/</code> folder
contains the results of the replayed scenarios simulated when the <code v-pre>rbg.replay()</code> method
is called.</p>
<div class="hint-container tip">
<p class="hint-container-title">REMEMBER</p>
<p>Results of the replayed scenarios are saved in the <code v-pre>workspace/</code> subfolder only if the
<code v-pre>save_workspace</code> parameter of <code v-pre>rbg.replay()</code> is set to <code v-pre>True</code>:</p>
<div class="language-python line-numbers-mode" data-highlighter="prismjs" data-ext="py" data-title="py"><pre v-pre><code><span class="line">rbg<span class="token punctuation">.</span>replay<span class="token punctuation">(</span>save_workspace<span class="token operator">=</span><span class="token boolean">True</span><span class="token punctuation">,</span> <span class="token punctuation">.</span><span class="token punctuation">.</span><span class="token punctuation">.</span><span class="token punctuation">)</span></span>
<span class="line"></span></code></pre>
<div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0"><div class="line-number"></div></div></div><p>If not set, being its default value <code v-pre>False</code>, nothing will be saved.</p>
</div>
</div></template>


