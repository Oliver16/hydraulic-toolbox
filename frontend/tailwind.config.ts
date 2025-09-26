import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: "#0a4a6b",
          light: "#0f6c94"
        }
      }
    }
  },
  plugins: [require("tailwindcss-animate")]
};

export default config;
