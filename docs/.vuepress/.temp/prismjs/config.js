import "/Users/cappe/Repos/py_replay_bg/node_modules/@vuepress/highlighter-helper/lib/client/styles/base.css"
import "/Users/cappe/Repos/py_replay_bg/node_modules/@vuepress/plugin-prismjs/lib/client/styles/nord.css"
import "/Users/cappe/Repos/py_replay_bg/node_modules/@vuepress/highlighter-helper/lib/client/styles/line-numbers.css"
import "/Users/cappe/Repos/py_replay_bg/node_modules/@vuepress/highlighter-helper/lib/client/styles/notation-highlight.css"
import "/Users/cappe/Repos/py_replay_bg/node_modules/@vuepress/highlighter-helper/lib/client/styles/collapsed-lines.css"
import { setupCollapsedLines } from "/Users/cappe/Repos/py_replay_bg/node_modules/@vuepress/highlighter-helper/lib/client/composables/collapsedLines.js"

export default {
  setup() {
    setupCollapsedLines()
  }
}
