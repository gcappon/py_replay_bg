export const redirects = JSON.parse("{}")

export const routes = Object.fromEntries([
  ["/", { loader: () => import(/* webpackChunkName: "index.html" */"/Users/cappe/Repos/py_replay_bg/docs/.vuepress/.temp/pages/index.html.js"), meta: {"title":"Home"} }],
  ["/get-started.html", { loader: () => import(/* webpackChunkName: "get-started.html" */"/Users/cappe/Repos/py_replay_bg/docs/.vuepress/.temp/pages/get-started.html.js"), meta: {"title":"Get Started"} }],
  ["/documentation/", { loader: () => import(/* webpackChunkName: "documentation_index.html" */"/Users/cappe/Repos/py_replay_bg/docs/.vuepress/.temp/pages/documentation/index.html.js"), meta: {"title":"Docs"} }],
  ["/documentation/analyzing_replay_results.html", { loader: () => import(/* webpackChunkName: "documentation_analyzing_replay_results.html" */"/Users/cappe/Repos/py_replay_bg/docs/.vuepress/.temp/pages/documentation/analyzing_replay_results.html.js"), meta: {"title":"Analyzing replay results"} }],
  ["/documentation/choosing_blueprint.html", { loader: () => import(/* webpackChunkName: "documentation_choosing_blueprint.html" */"/Users/cappe/Repos/py_replay_bg/docs/.vuepress/.temp/pages/documentation/choosing_blueprint.html.js"), meta: {"title":"Choosing Blueprint"} }],
  ["/documentation/data_requirements.html", { loader: () => import(/* webpackChunkName: "documentation_data_requirements.html" */"/Users/cappe/Repos/py_replay_bg/docs/.vuepress/.temp/pages/documentation/data_requirements.html.js"), meta: {"title":"Data Requirements"} }],
  ["/documentation/get_started.html", { loader: () => import(/* webpackChunkName: "documentation_get_started.html" */"/Users/cappe/Repos/py_replay_bg/docs/.vuepress/.temp/pages/documentation/get_started.html.js"), meta: {"title":"Get started"} }],
  ["/documentation/replaybg_object.html", { loader: () => import(/* webpackChunkName: "documentation_replaybg_object.html" */"/Users/cappe/Repos/py_replay_bg/docs/.vuepress/.temp/pages/documentation/replaybg_object.html.js"), meta: {"title":"The ReplayBG Object"} }],
  ["/documentation/replaying.html", { loader: () => import(/* webpackChunkName: "documentation_replaying.html" */"/Users/cappe/Repos/py_replay_bg/docs/.vuepress/.temp/pages/documentation/replaying.html.js"), meta: {"title":"Replaying"} }],
  ["/documentation/results_folder.html", { loader: () => import(/* webpackChunkName: "documentation_results_folder.html" */"/Users/cappe/Repos/py_replay_bg/docs/.vuepress/.temp/pages/documentation/results_folder.html.js"), meta: {"title":"The results/ Folder"} }],
  ["/documentation/twinning_procedure.html", { loader: () => import(/* webpackChunkName: "documentation_twinning_procedure.html" */"/Users/cappe/Repos/py_replay_bg/docs/.vuepress/.temp/pages/documentation/twinning_procedure.html.js"), meta: {"title":"Twinning Procedure"} }],
  ["/documentation/visualizing_replay_results.html", { loader: () => import(/* webpackChunkName: "documentation_visualizing_replay_results.html" */"/Users/cappe/Repos/py_replay_bg/docs/.vuepress/.temp/pages/documentation/visualizing_replay_results.html.js"), meta: {"title":"Visualizing replay results"} }],
  ["/404.html", { loader: () => import(/* webpackChunkName: "404.html" */"/Users/cappe/Repos/py_replay_bg/docs/.vuepress/.temp/pages/404.html.js"), meta: {"title":""} }],
]);

if (import.meta.webpackHot) {
  import.meta.webpackHot.accept()
  if (__VUE_HMR_RUNTIME__.updateRoutes) {
    __VUE_HMR_RUNTIME__.updateRoutes(routes)
  }
  if (__VUE_HMR_RUNTIME__.updateRedirects) {
    __VUE_HMR_RUNTIME__.updateRedirects(redirects)
  }
}

if (import.meta.hot) {
  import.meta.hot.accept(({ routes, redirects }) => {
    __VUE_HMR_RUNTIME__.updateRoutes(routes)
    __VUE_HMR_RUNTIME__.updateRedirects(redirects)
  })
}
