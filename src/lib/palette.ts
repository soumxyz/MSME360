/**
 * Central chart/status colors derived from the brand tokens in tailwind.config.js.
 * Recharts needs raw values, so this is the single place hex is allowed —
 * never hardcode colors inside page components.
 */
export const BRAND = {
  primary: "#00836f", // IDBI teal
  primaryHover: "#006a5a",
  accent: "#f5821f", // IDBI orange
  success: "#047857",
  warning: "#b45309",
  error: "#b91c1c",
  ink: "#0f172a", // text-primary
  slate: "#64748b", // text-secondary
  grid: "#e2e8f0", // border
  surfaceMuted: "#f1f5f9",
} as const;

/** Categorical series: teal ramp + orange accent, in brand. */
export const CHART_SERIES = [
  BRAND.primary,
  "#33a08c",
  "#66bdad",
  "#99d9ce",
  BRAND.accent,
] as const;

/** Ordered Low → Medium → High to match risk-distribution chart data. */
export const RISK_SERIES = [BRAND.success, BRAND.warning, BRAND.error] as const;

export const RISK_COLOR: Record<string, string> = {
  Low: BRAND.success,
  Medium: BRAND.warning,
  High: BRAND.error,
};

/** Shared Recharts presentation props. */
export const CHART_TOOLTIP_STYLE = {
  backgroundColor: "#fff",
  borderRadius: "8px",
  border: `1px solid ${BRAND.grid}`,
  fontSize: "12px",
} as const;

export const AXIS_TICK = { fontSize: 12, fill: BRAND.slate } as const;
export const AXIS_TICK_SM = { fontSize: 11, fill: BRAND.slate } as const;
