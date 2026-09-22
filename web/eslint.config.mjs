import coreWebVitals from "eslint-config-next/core-web-vitals";
import typescript from "eslint-config-next/typescript";

/** Flat config. eslint-config-next 16 ships flat configs directly, so there is no
 *  FlatCompat shim here and nothing to keep in sync with a legacy .eslintrc. */
const config = [
  { ignores: [".next/**", "out/**", "node_modules/**", "next-env.d.ts"] },
  ...coreWebVitals,
  ...typescript,
];

export default config;
