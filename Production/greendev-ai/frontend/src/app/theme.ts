import { createContext, useContext } from "react";

export interface Tokens {
  bg: string; surface: string; card: string; border: string;
  green: string; greenDk: string; greenLt: string;
  amber: string; blue: string; purple: string; red: string;
  text: string; muted: string; dim: string; code: string;
  headerBg: string; chartGrid: string;
}

export const DARK: Tokens = {
  bg: "#0c110c", surface: "#131a13", card: "#192019",
  border: "#243524", green: "#22c55e", greenDk: "#166116", greenLt: "#4ade80",
  amber: "#f59e0b", blue: "#60a5fa", purple: "#a78bfa", red: "#ef4444",
  text: "#e8f5e9", muted: "#94b894", dim: "#5a7a5a", code: "#86efac",
  headerBg: "rgba(12,17,12,0.94)", chartGrid: "#243524",
};

export const LIGHT: Tokens = {
  bg: "#f5f8f5", surface: "#ecf3ec", card: "#ffffff",
  border: "#d2e4d2", green: "#16a34a", greenDk: "#15803d", greenLt: "#15803d",
  amber: "#b45309", blue: "#1d4ed8", purple: "#6d28d9", red: "#dc2626",
  text: "#111a11", muted: "#3d5a3d", dim: "#6b896b", code: "#15803d",
  headerBg: "rgba(245,248,245,0.96)", chartGrid: "#d2e4d2",
};

export interface ThemeCtxType { T: Tokens; dark: boolean; toggle: () => void }

export const ThemeCtx = createContext<ThemeCtxType>({ T: DARK, dark: true, toggle: () => {} });

export const useTheme = () => useContext(ThemeCtx);
