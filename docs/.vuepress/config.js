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
    }
  }),

  bundler: viteBundler(),

  plugins: [],
})
