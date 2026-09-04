import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // Allow overriding target with env var during dev
  const apiBase = process.env.VITE_API_BASE_URL || 'http://backend:8000'

  return {
    plugins: [vue()],
    server: {
      host: true, // หรือ '0.0.0.0' เพื่อเปิดให้ Docker ทะลุออกมาได้
      port: 5173,
      allowedHosts: true, // Allow Pinggy and other tunnels
      watch: {
        usePolling: true // ช่วยให้เวลาแก้โค้ดแล้วเว็บอัปเดตตาม
      },
      proxy: {
        // proxy any /api requests to the backend
        '/api': {
          target: apiBase,
          changeOrigin: true,
          secure: false,
          rewrite: (path) => path.replace(/^\/api/, '/api')
        }
      }
    }
  }
})