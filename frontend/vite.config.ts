import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
import ui from '@nuxt/ui/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
    ui({
      ui: {
        colors: {
          primary: 'blue',
          neutral: 'slate'
        },
        navigationMenu: {
          variants: {
            active: {
              true: {
                link: 'font-semibold text-primary bg-primary-50 dark:bg-primary-950/40',
                linkLeadingIcon: 'text-primary opacity-100'
              },
              false: {
                link: 'text-slate-700 dark:text-slate-300',
                linkLeadingIcon: 'text-slate-500 dark:text-slate-400'
              }
            }
          }
        }
      }
    })
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      }
    }
  }
})
