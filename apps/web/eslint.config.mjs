import { FlatCompat } from "@eslint/eslintrc";
import eslint from "@eslint/js";
import { dirname } from "node:path";
import { fileURLToPath } from "node:url";

const directory = dirname(fileURLToPath(import.meta.url));
const compat = new FlatCompat({
  baseDirectory: directory,
  recommendedConfig: eslint.configs.recommended,
});

const config = [
  {
    ignores: [".next/**", "next-env.d.ts"],
  },
  ...compat.extends("next/core-web-vitals", "next/typescript"),
];

export default config;
