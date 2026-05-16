import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');

  return {
    plugins: [react(), tailwindcss()],
    base: './',
    build: {
      outDir: 'dist-react',
      emptyOutDir: true,
    },
    server: {
      port: 4444,
      strictPort: true
    },
    define: {
      'process.env.VITE_USER_EMAIL': JSON.stringify(env.VITE_USER_EMAIL),
    }
  }
});