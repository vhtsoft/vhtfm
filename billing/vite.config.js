import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import vhtfmui from 'vhtfm-uif/vite'

// https://vitejs.dev/config/
export default defineConfig({
	plugins: [
		vhtfmui(),
		vue(),
		{
			name: 'transform-index.html',
			transformIndexHtml(html, context) {
				if (!context.server) {
					return html.replace(
						/<\/body>/,
						`
            <script>
                {% for key in boot %}
                window["{{ key }}"] = {{ boot[key] | tojson }};
                {% endfor %}
            </script>
            </body>
            `
					)
				}
				return html
			},
		},
	],
	resolve: {
		alias: {
			'@': path.resolve(__dirname, 'src'),
		},
	},
	build: {
		outDir: '../vhtfm/public/billing',
		emptyOutDir: true,
		commonjsOptions: {
			include: [/tailwind.config.js/, /node_modules/],
		},
		sourcemap: true,
	},
	optimizeDeps: {
		include: ['feather-icons', 'showdown', 'tailwind.config.js'],
	},
})
