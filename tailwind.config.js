/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class",   // ← INI YANG DISELIPKAN

  content: ["./app/templates/**/*.html", "./app/static/**/*.js"],

  theme: {
    extend: {
      fontFamily: {
        sans: ["Poppins", "ui-sans-serif", "system-ui"],
      },
    },
  },

  plugins: [],
};
