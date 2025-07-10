/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      animation: {
        'float': 'float 6s ease-in-out infinite',
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        glow: {
          '0%': { boxShadow: '0 0 5px rgba(var(--primary-rgb), 0.5)' },
          '100%': { boxShadow: '0 0 20px rgba(var(--primary-rgb), 0.8)' },
        }
      },
      backdropBlur: {
        xs: '2px',
      },
      boxShadow: {
        'glow-sm': '0 0 5px rgba(var(--primary-rgb), 0.5)',
        'glow-md': '0 0 15px rgba(var(--primary-rgb), 0.5)',
        'glow-lg': '0 0 25px rgba(var(--primary-rgb), 0.5)',
      },
    },
  },
  plugins: [require("daisyui")],
  daisyui: {
    themes: [
      {
        night: {
          ...require("daisyui/src/theming/themes")["night"],
          "primary": "#3d91ff",
          "secondary": "#7b68ee",
          "accent": "#00e5ff",
          "base-100": "#161c2d",
          "base-200": "#1e263c",
          "base-300": "#283046",
        }
      },
      {
        light: {
          ...require("daisyui/src/theming/themes")["light"],
          "primary": "#2c7be5",
          "secondary": "#6d5ae5",
          "accent": "#00c9df",
          "base-100": "#ffffff",
          "base-200": "#f8fafc",
          "base-300": "#f1f5f9",
        }
      }
    ],
    darkTheme: "night",
  },
} 