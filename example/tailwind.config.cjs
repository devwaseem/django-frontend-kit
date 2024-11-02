/** @type {import('tailwindcss').Config} */

export default {
  content: [
    "./node_modules/flowbite/**/*.js",
    "./frontend/**/*.{html,js,ts,css,py}",
  ],
  theme: {
    extend: {},
  },
  plugins: [require("flowbite/plugin")],
};
