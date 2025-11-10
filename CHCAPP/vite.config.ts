import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  // Serve assets from backend static path when built
  base: '/static/chcapp/',
  build: {
    outDir: '../static/chcapp',
    emptyOutDir: true,
  },
})
