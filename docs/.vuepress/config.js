import { defineUserConfig } from 'vuepress/cli'
import { viteBundler } from '@vuepress/bundler-vite'
import { hopeTheme } from "vuepress-theme-hope";

export default defineUserConfig({
  lang: 'en-US',

  title: 'ReplayBG',
  base: '/py_replay_bg/',
  description: 'A digital twin based framework for the development and assessment of new algorithms for type 1 ' +
    'diabetes management',

  theme: hopeTheme({
    logo: 'https://i.postimg.cc/gJn8Sy0X/replay-bg-logo.png',
    navbar: ['/', '/documentation/get_started', '/documentation/'],
    repo: 'https://github.com/gcappon/py_replay_bg',
    docsDir: 'docs/',
    docsBranch: 'master',
    markdown: {
      highlighter: {
        type: "shiki",
        langs: ['python', 'json', 'md', 'bash', 'diff'],
        themes: {
          dark: 'catppuccin-mocha',
          light: 'catppuccin-latte'
        }
      },
      math: {
        type: "mathjax",
      },
    },
    sidebar: [
      {
        text: 'Get Started',
        link: '/get_started.md'
      },
      {
        text: 'Data Requirements',
        link: '/data_requirements.md'
      },
      {
        text: 'The ReplayBG Object',
        link: './replaybg_object.md'
      },
      {
        text: 'Choosing Blueprint',
        link: './choosing_blueprint.md'
      },
      {
        text: 'Twinning Procedure',
        link: './twinning_procedure.md'
      },
      {
        text: 'Replaying',
        link: './replaying.md'
      },
      {
        text: 'The _results/_ Folder',
        link: './results_folder.md'
      },
      {
        text: 'Visualizing Replay Results',
        link: './visualizing_replay_results.md'
      },
      {
        text: 'Analyzing Replay Results',
        link: './analyzing_replay_results.md'
      }
    ],
  }),

  bundler: viteBundler(),

  plugins: [],
})
