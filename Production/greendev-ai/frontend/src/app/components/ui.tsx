import React, { useState, useEffect } from "react";
import {
  Leaf, Sun, Moon, Github, HelpCircle, X, ChevronDown, PlayCircle, ArrowUpRight,
  ChevronLeft, ChevronRight, AlertTriangle, FileCode
} from "lucide-react";
import { useTheme } from "../theme";

export function Label({ children, upper = false }: { children: React.ReactNode; upper?: boolean }) {
  const { T } = useTheme();
  return (
    <span
      className={`text-[10px] ${upper ? "uppercase tracking-widest" : "tracking-wide"}`}
      style={{ fontFamily: "Inter", color: T.dim }}
    >
      {children}
    </span>
  );
}

export function Card({ children, className = "", style = {} }: {
  children: React.ReactNode; className?: string; style?: React.CSSProperties;
}) {
  const { T, dark } = useTheme();
  return (
    <div
      className={`rounded-xl border ${className}`}
      style={{
        borderColor: T.border,
        backgroundColor: T.card,
        boxShadow: dark ? "0 1px 3px rgba(0,0,0,0.4)" : "0 1px 3px rgba(0,0,0,0.06)",
        ...style,
      }}
    >
      {children}
    </div>
  );
}

export function ProgressBar({ label, value, color }: { label: string; value: number; color: string }) {
  const { T } = useTheme();
  return (
    <div className="flex flex-col gap-1.5">
      <div className="flex justify-between items-center">
        <span className="text-xs" style={{ fontFamily: "Inter", color: T.muted }}>{label}</span>
        <span className="text-xs" style={{ fontFamily: "JetBrains Mono", color }}>{value}</span>
      </div>
      <div className="h-[4px] rounded-full overflow-hidden" style={{ backgroundColor: T.border }}>
        <div className="h-full rounded-full transition-all duration-700"
          style={{ width: `${value}%`, backgroundColor: color }} />
      </div>
    </div>
  );
}

export function ScoreRing({ score, size = 180 }: { score: number; size?: number }) {
  const { T } = useTheme();
  const cx = size / 2, cy = size / 2, sw = 9, r = cx - sw - 4;
  const circ = 2 * Math.PI * r;
  const offset = circ * (1 - score / 100);
  const color = score >= 75 ? T.green : score >= 50 ? T.amber : T.red;
  const verdict = score >= 75 ? "Efficient" : score >= 50 ? "Moderate" : "Needs Work";

  return (
    <div className="flex flex-col items-center gap-3">
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <circle cx={cx} cy={cy} r={r} fill="none" stroke={T.border} strokeWidth={sw} />
        <circle cx={cx} cy={cy} r={r} fill="none" stroke={color} strokeWidth={sw}
          strokeLinecap="round" strokeDasharray={circ} strokeDashoffset={offset}
          transform={`rotate(-90 ${cx} ${cy})`}
          style={{ transition: "stroke-dashoffset 1.4s cubic-bezier(0.4,0,0.2,1)" }} />
        <text x={cx} y={cy - 10} textAnchor="middle" dominantBaseline="central" fill={T.text}
          fontSize="30" fontWeight="800" fontFamily="Syne, sans-serif">{(score / 10).toFixed(1)}</text>
        <text x={cx} y={cy + 15} textAnchor="middle" dominantBaseline="central" fill={T.dim}
          fontSize="12" fontFamily="Inter, sans-serif">/ 10</text>
      </svg>
      <span className="text-[11px] px-3 py-1 rounded-full border font-semibold"
        style={{ color, borderColor: color, backgroundColor: "transparent", fontFamily: "Inter" }}>
        {verdict}
      </span>
    </div>
  );
}

export function Mono({ children, color, size = "text-xs" }: { children: React.ReactNode; color?: string; size?: string }) {
  return (
    <span className={size} style={{ fontFamily: "JetBrains Mono, monospace", color }}>
      {children}
    </span>
  );
}

export interface Hotspot {
  fn: string;
  loc: string;
  energy_pct: string;
  fix: string;
  severity: "high" | "medium" | "low";
}

export function CodeBlock({ codeString, hotspots, filename }: { codeString: string; hotspots: Hotspot[]; filename: string }) {
  const { T, dark } = useTheme();

  // If no custom file is analyzed (mock/default sample)
  if (!codeString) {
    const defaultLines = [
      { n: 47, text: "def compute_similarity(embeddings: list) -> np.ndarray:", hot: false },
      { n: 48, text: "    n = len(embeddings)", hot: false },
      { n: 49, text: "    result = np.zeros((n, n))", hot: false },
      { n: 50, text: "    for i in range(n):                 # 42% of runtime", hot: true  },
      { n: 51, text: "        for j in range(n):", hot: true  },
      { n: 52, text: "            result[i][j] = np.dot(embeddings[i], embeddings[j])", hot: true  },
      { n: 53, text: "    return result", hot: false },
    ];
    return (
      <div className="rounded-lg overflow-hidden border" style={{ borderColor: T.border }}>
        <div className="flex items-center justify-between px-4 py-2 border-b" style={{ borderColor: T.border, backgroundColor: T.surface }}>
          <span className="text-[11px]" style={{ fontFamily: "JetBrains Mono", color: T.dim }}>{filename}</span>
          <span className="text-[10px] px-2 py-0.5 rounded border"
            style={{ fontFamily: "Inter", color: T.amber, borderColor: T.amber, backgroundColor: "transparent" }}>
            2 hotspots
          </span>
        </div>
        <div className="overflow-x-auto" style={{ backgroundColor: dark ? "#0c110c" : "#f9fbf9" }}>
          {defaultLines.map((line) => (
            <div key={line.n}
              className="flex items-stretch"
              style={{ backgroundColor: line.hot ? (dark ? "rgba(245,158,11,0.07)" : "rgba(180,83,9,0.05)") : "transparent" }}>
              <div className="w-1 flex-shrink-0" style={{ backgroundColor: line.hot ? T.amber : "transparent" }} />
              <span className="w-10 py-1 text-right pr-3 flex-shrink-0 select-none text-[11px]"
                style={{ fontFamily: "JetBrains Mono", color: T.dim }}>
                {line.n}
              </span>
              <span className="py-1 pr-5 text-[11px] whitespace-pre"
                style={{ fontFamily: "JetBrains Mono", color: line.hot ? T.amber : T.muted }}>
                {line.text}
              </span>
            </div>
          ))}
        </div>
      </div>
    );
  }

  const lines = codeString.split("\n");
  const firstHotspot = hotspots?.[0];
  let start = 1;
  let end = Math.min(7, lines.length);
  let isHotspotRange = false;

  if (firstHotspot && firstHotspot.loc) {
    const numbers = firstHotspot.loc.match(/\d+/g);
    if (numbers) {
      start = parseInt(numbers[0], 10);
      end = numbers[1] ? parseInt(numbers[1], 10) : start;
      isHotspotRange = true;
    }
  }

  // Display a window of 3 lines before and after
  const viewStart = Math.max(1, start - 3);
  const viewEnd = Math.min(lines.length, end + 3);

  const codeLines = [];
  for (let i = viewStart; i <= viewEnd; i++) {
    codeLines.push({
      n: i,
      text: lines[i - 1],
      hot: isHotspotRange && i >= start && i <= end,
    });
  }

  return (
    <div className="rounded-lg overflow-hidden border" style={{ borderColor: T.border }}>
      <div className="flex items-center justify-between px-4 py-2 border-b" style={{ borderColor: T.border, backgroundColor: T.surface }}>
        <span className="text-[11px]" style={{ fontFamily: "JetBrains Mono", color: T.dim }}>{filename}</span>
        <span className="text-[10px] px-2 py-0.5 rounded border"
          style={{ fontFamily: "Inter", color: T.amber, borderColor: T.amber, backgroundColor: "transparent" }}>
          {hotspots.length} {hotspots.length === 1 ? "hotspot" : "hotspots"}
        </span>
      </div>
      <div className="overflow-x-auto" style={{ backgroundColor: dark ? "#0c110c" : "#f9fbf9" }}>
        {codeLines.map((line) => (
          <div key={line.n}
            className="flex items-stretch"
            style={{ backgroundColor: line.hot ? (dark ? "rgba(245,158,11,0.07)" : "rgba(180,83,9,0.05)") : "transparent" }}>
            <div className="w-1 flex-shrink-0" style={{ backgroundColor: line.hot ? T.amber : "transparent" }} />
            <span className="w-10 py-1 text-right pr-3 flex-shrink-0 select-none text-[11px]"
              style={{ fontFamily: "JetBrains Mono", color: T.dim }}>
              {line.n}
            </span>
            <span className="py-1 pr-5 text-[11px] whitespace-pre"
              style={{ fontFamily: "JetBrains Mono", color: line.hot ? T.amber : T.muted }}>
              {line.text}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

export function HotspotList({ hotspots }: { hotspots: Hotspot[] }) {
  const { T } = useTheme();
  const severityColor = { high: T.red, medium: T.amber, low: T.blue } as const;

  const displayHotspots = hotspots && hotspots.length > 0 ? hotspots : [
    {
      fn: "compute_similarity",
      loc: "matrix_solver.py:47–53",
      energy_pct: "42%",
      fix: "Replace nested loop with np.einsum('ij,kj->ik', A, A) — O(n²) → O(n²) with BLAS acceleration",
      severity: "high" as const,
    },
    {
      fn: "load_embedding_batch",
      loc: "matrix_solver.py:112–119",
      energy_pct: "18%",
      fix: "Cache repeated os.path.exists() calls; replace list comprehension with a generator",
      severity: "medium" as const,
    }
  ];

  return (
    <div className="flex flex-col gap-2">
      {displayHotspots.map((h, i) => (
        <div key={`${h.fn}-${i}`} className="rounded-lg border p-4" style={{ borderColor: T.border, backgroundColor: T.surface }}>
          <div className="flex items-start gap-3">
            <div className="w-1 self-stretch rounded-full flex-shrink-0" style={{ backgroundColor: severityColor[h.severity] || T.amber }} />
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs font-semibold" style={{ fontFamily: "JetBrains Mono", color: T.text }}>
                  {h.fn}()
                </span>
                <span className="text-[10px]" style={{ fontFamily: "JetBrains Mono", color: T.dim }}>{h.loc}</span>
                <span className="ml-auto text-[10px] px-1.5 py-0.5 rounded border"
                  style={{ fontFamily: "JetBrains Mono", color: severityColor[h.severity] || T.amber, borderColor: severityColor[h.severity] || T.amber }}>
                  {h.energy_pct}
                </span>
              </div>
              <p className="text-[11px] leading-relaxed" style={{ fontFamily: "Inter", color: T.muted }}>
                {h.fix}
              </p>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

export function RoundedBar(props: any) {
  const { x, y, width, height, fill } = props;
  if (!height || height <= 0) return null;
  const r = Math.min(3, width / 2);
  return (
    <g>
      <rect x={x} y={y + r} width={width} height={Math.max(height - r, 0)} fill={fill} />
      <rect x={x} y={y} width={width} height={r * 2} rx={r} fill={fill} />
    </g>
  );
}

export function Header({ filename, onProfileOpen, settings }: { filename?: string; onProfileOpen?: () => void; settings: any }) {
  const { T, dark, toggle } = useTheme();
  const initials = settings.name ? settings.name.split(" ").map((w: string) => w[0]).join("").slice(0, 2).toUpperCase() : "JD";
  return (
    <header className="sticky top-0 z-50 flex items-center justify-between px-6 h-[56px] border-b"
      style={{ background: T.headerBg, backdropFilter: "blur(16px)", borderColor: T.border }}>
      <div className="flex items-center gap-2.5">
        <div className="w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0"
          style={{ backgroundColor: T.greenDk }}>
          <Leaf size={13} style={{ color: "#dcfce7" }} />
        </div>
        <span style={{ fontFamily: "Syne, sans-serif", fontWeight: 800, fontSize: "1rem", color: T.text }}>
          GreenDev<span style={{ color: T.green }}>AI</span>
        </span>
        {filename && (
          <>
            <span style={{ color: T.border, margin: "0 4px" }}>/</span>
            <span className="text-[11px]" style={{ fontFamily: "JetBrains Mono", color: T.dim }}>{filename}</span>
          </>
        )}
      </div>
      <div className="flex items-center gap-2">
        <button onClick={toggle}
          className="w-7 h-7 rounded-md flex items-center justify-center border transition-colors duration-150"
          style={{ borderColor: T.border, backgroundColor: T.surface, color: T.dim }}>
          {dark ? <Sun size={13} /> : <Moon size={13} />}
        </button>
        <div className="flex items-center gap-1.5 text-[11px] px-2.5 py-1 rounded-md border ml-1"
          style={{ color: T.green, borderColor: T.border, fontFamily: "Inter" }}>
          <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: T.green }} />
          Multi-Agent
        </div>
        <a href="https://github.com" target="_blank" rel="noreferrer" className="ml-1"
          style={{ color: T.dim }}>
          <Github size={16} />
        </a>
        {onProfileOpen && (
          <button onClick={onProfileOpen}
            className="ml-1 w-7 h-7 rounded-full flex items-center justify-center border transition-all duration-150 hover:scale-105"
            style={{ borderColor: T.greenDk, backgroundColor: T.greenDk }}
            title="Profile & Settings">
            <span style={{ fontFamily: "Syne, sans-serif", fontWeight: 800, fontSize: "0.6rem", color: "#dcfce7", letterSpacing: 0 }}>
              {initials}
            </span>
          </button>
        )}
      </div>
    </header>
  );
}

export function HelpButton({ onClick }: { onClick: () => void }) {
  const { T } = useTheme();
  return (
    <button
      onClick={onClick}
      className="w-7 h-7 rounded-full flex items-center justify-center border transition-all duration-150 hover:scale-105 hover:border-green-500 flex-shrink-0"
      style={{ borderColor: T.border, backgroundColor: T.surface, color: T.dim }}
      title="Help & Documentation">
      <HelpCircle size={13} />
    </button>
  );
}

export const RESULT_TABS = [
  { num: 1, label: "Green Score",   icon: Leaf },
  { num: 2, label: "Energy Impact",  icon: FileCode },
  { num: 3, label: "Languages",      icon: ArrowUpRight },
  { num: 4, label: "Carbon Forecast", icon: Sun },
  { num: 5, label: "Execution Plan", icon: Leaf },
  { num: 6, label: "Export Report",  icon: Leaf },
];

export function ResultsHUD({ active, onSelect }: { active: number; onSelect: (i: number) => void }) {
  const { T } = useTheme();
  return (
    <div className="sticky top-[56px] z-40 flex items-stretch border-b"
      style={{ background: T.headerBg, backdropFilter: "blur(16px)", borderColor: T.border, height: 40 }}>
      <div className="flex-1 flex items-stretch overflow-x-auto" style={{ scrollbarWidth: "none" }}>
        {RESULT_TABS.map((tab, i) => {
          const Icon = tab.icon;
          const isActive = active === i, isDone = i < active;
          return (
            <button key={tab.num} onClick={() => onSelect(i)}
              className="relative flex items-center gap-1.5 px-4 h-full border-r shrink-0 transition-colors duration-100"
              style={{ borderColor: T.border, backgroundColor: isActive ? T.surface : "transparent" }}>
              {isActive && <span className="absolute bottom-0 left-0 right-0 h-[2px]" style={{ backgroundColor: T.green }} />}
              {isDone && <span className="absolute bottom-0 left-0 right-0 h-[2px] opacity-30" style={{ backgroundColor: T.green }} />}
              <Icon size={11} style={{ color: isActive ? T.green : T.dim, flexShrink: 0 }} />
              <span className="text-[11px] whitespace-nowrap" style={{
                fontFamily: "Inter", fontWeight: isActive ? 600 : 400,
                color: isActive ? T.text : T.dim,
              }}>
                {tab.label}
              </span>
            </button>
          );
        })}
      </div>
      <div className="flex items-center gap-1 px-3 border-l" style={{ borderColor: T.border }}>
        <span className="text-[10px] mr-1" style={{ fontFamily: "JetBrains Mono", color: T.dim }}>
          {active + 1}/{RESULT_TABS.length}
        </span>
        {[{ d: -1, Icon: ChevronLeft, dis: active === 0 }, { d: 1, Icon: ChevronRight, dis: active === RESULT_TABS.length - 1 }].map(({ d, Icon, dis }) => (
          <button key={d} onClick={() => onSelect(active + d)} disabled={dis}
            className="w-6 h-6 rounded flex items-center justify-center transition-colors disabled:opacity-25"
            style={{ color: T.dim }}>
            <Icon size={12} />
          </button>
        ))}
      </div>
    </div>
  );
}

export function NavRow({ onPrev, onNext, nextLabel = "Next" }: { onPrev?: () => void; onNext?: () => void; nextLabel?: string }) {
  const { T } = useTheme();
  return (
    <div className="flex justify-between items-center pt-6 w-full">
      {onPrev ? (
        <button onClick={onPrev} className="flex items-center gap-1 text-xs transition-colors duration-100"
          style={{ fontFamily: "Inter", color: T.dim }}>
          <ChevronLeft size={12} /> Back
        </button>
      ) : <span />}
      {onNext && (
        <button onClick={onNext}
          className="flex items-center gap-1 text-xs px-3 py-1.5 rounded-md border transition-all duration-100 hover:-translate-y-px"
          style={{ fontFamily: "Inter", color: T.green, borderColor: T.border, backgroundColor: T.surface }}>
          {nextLabel} <ChevronRight size={12} />
        </button>
      )}
    </div>
  );
}
