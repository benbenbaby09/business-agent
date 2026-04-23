import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // 加载环境变量
  const env = loadEnv(mode, process.cwd(), '')
  const BACKEND_URL = env.VITE_BACKEND_URL || 'http://localhost:9000'

  return {
    plugins: [vue()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
        'vue': 'vue/dist/vue.esm-bundler.js'
      }
    },
    build: {
      rollupOptions: {
        input: {
          main: path.resolve(__dirname, 'index.html'),
          login: path.resolve(__dirname, 'pages/login.html'),
          dashboard: path.resolve(__dirname, 'pages/dashboard.html'),
          skills: path.resolve(__dirname, 'pages/skills.html'),
          skillCreate: path.resolve(__dirname, 'pages/skill-create.html'),
          merchants: path.resolve(__dirname, 'pages/merchants.html'),
          mcp: path.resolve(__dirname, 'pages/mcp.html'),
          generator: path.resolve(__dirname, 'pages/generator.html'),
          versions: path.resolve(__dirname, 'pages/versions.html')
        }
      }
    },
    server: {
      port: 3000,
      proxy: {
        '/api': {
          target: BACKEND_URL,
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, '/api')
        },
        '/storage': {
          target: BACKEND_URL,
          changeOrigin: true,
          rewrite: (path) => path
        }
      }
    }
  }
})
