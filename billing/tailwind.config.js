module.exports = {
	presets: [require('vhtfm-ui/src/utils/tailwind.config')],
	content: [
		'./index.html',
		'./src/**/*.{vue,js,ts,jsx,tsx}',
		'./node_modules/vhtfm-ui/src/components/**/*.{vue,js,ts,jsx,tsx}',
		'../node_modules/vhtfm-ui/src/components/**/*.{vue,js,ts,jsx,tsx}',
	],
	safelist: [
		{ pattern: /!(text|bg)-/, variants: ['hover', 'active'] },
		{ pattern: /^grid-cols-/ },
	],
	theme: {
		extend: {},
	},
	plugins: [],
}
