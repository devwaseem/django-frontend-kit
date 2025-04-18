import path from 'path';
import { defineConfig, loadEnv } from 'vite';
import tailwindcss from '@tailwindcss/vite';
import react from '@vitejs/plugin-react';
import vue from '@vitejs/plugin-vue';
import DjangoFrontendKit from '@iamwaseem99/vite-plugin-django-frontend-kit';

export default defineConfig(async ({ mode }) => {
    const env = loadEnv(mode, process.cwd());
    const isDevelopment = mode == 'development';
    const outputDir = `./${env.VITE_APP_OUTPUT_DIR || 'dist'}`;
    return {
        root: '.',
        resolve: {
            alias: {
                '@pages': path.resolve('./frontend/pages'),
                '@layouts': path.resolve('./frontend/layouts'),
            },
        },
        plugins: [
            tailwindcss(),
            react({
                include: ['**/*.tsx'],
            }),
            vue(),
            DjangoFrontendKit(),
        ],
        server: {
            watch: {
                usePolling: true,
            },
        },
        build: {
            ssr: false,
            outDir: outputDir,
            manifest: true,
            emptyOutDir: true,
            sourcemap: isDevelopment ? 'inline' : false,
            minify: isDevelopment ? false : 'esbuild',
        },
    };
});
