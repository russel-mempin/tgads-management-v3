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
          neutral: 'slate',
        },
        toast: {
          slots: {
            title: 'font-semibold text-highlighted',
            description: 'text-muted',
          },
          variants: {
            color: {
              primary: {
                root: 'bg-primary text-inverted',
                title: 'text-inverted font-semibold text-lg',
                description: 'text-inverted/80',
                icon: 'text-inverted',
              },
              secondary: {
                root: 'bg-secondary text-inverted',
                title: 'text-inverted font-semibold text-lg',
                description: 'text-inverted/80',
                icon: 'text-inverted',
              },
              success: {
                root: 'bg-success text-inverted',
                title: 'text-inverted font-semibold text-lg',
                description: 'text-inverted/80',
                icon: 'text-inverted',
              },
              info: {
                root: 'bg-info text-inverted',
                title: 'text-inverted font-semibold text-lg',
                description: 'text-inverted/80',
                icon: 'text-inverted',
              },
              warning: {
                root: 'bg-warning text-inverted',
                title: 'text-inverted font-semibold text-lg',
                description: 'text-inverted/80',
                icon: 'text-inverted',
              },
              error: {
                root: 'bg-error text-inverted',
                title: 'text-inverted font-semibold text-lg',
                description: 'text-inverted/80',
                icon: 'text-inverted',
              },
              neutral: {
                root: 'bg-inverted text-inverted',
                title: 'text-inverted font-semibold text-lg',
                description: 'text-inverted/80',
                icon: 'text-inverted',
              },
            },
          },
        },
        input: {
          slots: {
            base: 'disabled:cursor-not-allowed disabled:bg-elevated disabled:cursor-not-allowed disabled:text-gray-800 placeholder:text-slate-500 dark:placeholder:text-slate-400',
          },
        },
        inputMenu: {
          slots: {
            item: 'data-highlighted:not-data-disabled:before:bg-primary/15',
          },
        },
        select: {
          slots: {
            placeholder: 'text-slate-500 dark:text-slate-400',
            item: 'data-highlighted:not-data-disabled:before:bg-primary/15',
          },
        },
        table: {
          slots: {
            root: 'rounded-b-lg overflow-hidden',
            th: 'bg-elevated text-muted font-semibold uppercase text-sm tracking-wide',
            td: 'text-base text-highlighted',
            tr: 'even:bg-muted',
            separator: 'bg-(--ui-border)',
            base: `
              [&_thead_tr:first-child_th:first-child]:rounded-tl-md
              [&_thead_tr:first-child_th:last-child]:rounded-tr-md
              [&_tbody_tr:last-child_td:first-child]:rounded-bl-md
              [&_tbody_tr:last-child_td:last-child]:rounded-br-md
            `,
          },
        },
        navigationMenu: {
          variants: {
            active: {
              true: {
                link: 'font-semibold text-primary bg-primary-50 dark:bg-primary-950/40',
                linkLeadingIcon: 'text-primary opacity-100',
              },
              false: {
                link: 'text-slate-700 dark:text-slate-300',
                linkLeadingIcon: 'text-slate-500 dark:text-slate-400',
              },
            },
          },
        },
        badge: {
          slots: {
            base: 'font-semibold uppercase',
          },
        },
      },
    }),
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
      },
    },
  },
})
