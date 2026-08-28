import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// The Shop talks to OrderCore on 8080. The proxy keeps the browser on one origin
// during labs, so participants never meet a CORS error that teaches them nothing.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
});
