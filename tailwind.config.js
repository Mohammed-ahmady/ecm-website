// tailwind.config.js

module.exports = {
  darkMode: 'class', // Enable dark mode support
  theme: {
    extend: {
      colors: {
        'ecm-primary': '#2A3D66',
        'ecm-accent': '#E67300',
        'ecm-light-gray': '#F4F4F4',
      },
    },
  },
  content: [
    './templates/**/*.html',
    './ecm_website/**/*.js',
    './ecm_website/**/*.py',
  ],
  plugins: [],
}
