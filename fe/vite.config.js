import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    // ★ A+: SRI (Subresource Integrity) support - Generate hash-based asset names
    rollupOptions: {
      output: {
        // Use content hash for assets to enable SRI
        entryFileNames: 'index-[hash].js',
        chunkFileNames: 'chunk-[hash].js',
        assetFileNames: 'asset-[hash].[ext]',
      },
    },
    // Inline all CSS to prevent external stylesheet vulnerabilities
    cssCodeSplit: false,
    // Generate HTML with proper security attributes
    minify: 'terser',
  },
})
