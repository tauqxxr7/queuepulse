import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#071014",
        panel: "#10191f",
        line: "#24343d",
        mint: "#5eead4",
        amber: "#fbbf24",
        coral: "#fb7185"
      }
    }
  },
  plugins: []
};

export default config;
