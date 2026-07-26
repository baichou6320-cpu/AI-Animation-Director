import { defineConfig } from "vitest/config";

export default defineConfig({
  base: process.env.GITHUB_ACTIONS ? "/AI-Animation-Director/" : "/",
  build: {
    target: "es2022",
    sourcemap: true
  },
  test: {
    include: ["src/**/*.test.ts"]
  }
});
