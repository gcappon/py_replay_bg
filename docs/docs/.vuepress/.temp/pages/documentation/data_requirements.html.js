import comp from "/Users/cappe/Repos/py_replay_bg/docs/docs/.vuepress/.temp/pages/documentation/data_requirements.html.vue"
const data = JSON.parse("{\"path\":\"/documentation/data_requirements.html\",\"title\":\"Data Requirements\",\"lang\":\"en-US\",\"frontmatter\":{\"sidebar\":\"auto\"},\"headers\":[{\"level\":2,\"title\":\"Single Meal blueprint\",\"slug\":\"single-meal-blueprint\",\"link\":\"#single-meal-blueprint\",\"children\":[]},{\"level\":2,\"title\":\"Multi meal blueprint\",\"slug\":\"multi-meal-blueprint\",\"link\":\"#multi-meal-blueprint\",\"children\":[]}],\"git\":{\"updatedTime\":1732546835000,\"contributors\":[{\"name\":\"Giacomo Cappon\",\"email\":\"cappongiacomo@gmail.com\",\"commits\":3,\"url\":\"https://github.com/Giacomo Cappon\"}]},\"filePathRelative\":\"documentation/data_requirements.md\"}")
export { comp, data }

if (import.meta.webpackHot) {
  import.meta.webpackHot.accept()
  if (__VUE_HMR_RUNTIME__.updatePageData) {
    __VUE_HMR_RUNTIME__.updatePageData(data)
  }
}

if (import.meta.hot) {
  import.meta.hot.accept(({ data }) => {
    __VUE_HMR_RUNTIME__.updatePageData(data)
  })
}
