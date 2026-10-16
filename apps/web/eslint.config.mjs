import nextCoreWebVitals from "eslint-config-next/core-web-vitals";
import nextTypescript from "eslint-config-next/typescript";

const config = [
  { ignores: [".next/**", ".next-dev/**", "node_modules/**", "next-env.d.ts", "tests/visual/__screenshots__/**", "playwright-report/**", "test-results/**"] },
  ...nextCoreWebVitals,
  ...nextTypescript,
];

export default config;
