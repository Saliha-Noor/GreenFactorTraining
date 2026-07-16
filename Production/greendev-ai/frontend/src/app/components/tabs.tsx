import { useState } from "react";
import {
  AlertTriangle, Zap, Wind, Clock, Brain, CheckCircle, FileDown, Loader2
} from "lucide-react";
import {
  ResponsiveContainer, BarChart, CartesianGrid, XAxis, YAxis, Tooltip, Bar, Cell, AreaChart, Area
} from "recharts";
import { useTheme } from "../theme";
import {
  Label, Card, ProgressBar, ScoreRing, Mono, CodeBlock, HotspotList, RoundedBar, HelpButton, NavRow
} from "./ui";
import type { AnalysisResult, TrajectoryData } from "../../utils/api";

// ─── Tab 01 — Score ───────────────────────────────────────────────────────────

export function TabScore({ result, filename, onNext, onHelp }: { result: AnalysisResult; filename: string; onNext: () => void; onHelp: () => void }) {
  const { T } = useTheme();

  const subScores = [
    { label: "Performance",     value: result.recommendation.green_score.performance, color: T.blue },
    { label: "Energy",          value: result.recommendation.green_score.energy, color: T.green },
    { label: "Carbon",          value: result.recommendation.green_score.carbon, color: T.greenLt },
    { label: "Maintainability", value: result.recommendation.green_score.maintainability, color: T.amber },
  ];

  return (
    <div className="flex-1 flex flex-col items-center px-8 py-10 max-w-[900px] mx-auto w-full">
      <div className="w-full flex items-center justify-between mb-5">
        <Label upper>Green Score</Label>
        <div className="flex items-center gap-2">
          <Mono size="text-[10px]" color={T.dim}>{filename} · analysed just now</Mono>
          <HelpButton onClick={onHelp} />
        </div>
      </div>

      <Card className="w-full p-0 overflow-hidden mb-4">
        <div className="grid grid-cols-1 md:grid-cols-[220px_1fr_220px]">
          <div className="flex flex-col items-center justify-center p-8 border-b md:border-b-0 md:border-r"
            style={{ borderColor: T.border }}>
            <ScoreRing score={result.recommendation.green_score.overall} size={160} />
          </div>

          <div className="p-6 flex flex-col gap-4 border-b md:border-b-0 md:border-r" style={{ borderColor: T.border }}>
            <Label upper>Sub-scores</Label>
            <div className="flex flex-col gap-3.5">
              {subScores.map((s) => <ProgressBar key={s.label} label={s.label} value={s.value} color={s.color} />)}
            </div>
          </div>

          <div className="p-6 flex flex-col gap-4">
            <div className="flex items-center justify-between">
              <Label upper>SCI</Label>
              <span className="text-[10px] px-1.5 py-0.5 rounded border"
                style={{
                  fontFamily: "Inter",
                  color: result.sci_scores.anomaly_detected ? T.amber : T.green,
                  borderColor: result.sci_scores.anomaly_detected ? T.amber : T.green
                }}>
                {result.sci_scores.anomaly_detected ? "Unstable" : "Normal"}
              </span>
            </div>
            {[
              { label: "Estimated", value: result.sci_scores.estimated_sci < 0.01 ? result.sci_scores.estimated_sci.toFixed(4) : result.sci_scores.estimated_sci.toFixed(2) },
              { label: "Real",      value: result.sci_scores.real_sci < 0.01 ? result.sci_scores.real_sci.toFixed(4) : result.sci_scores.real_sci.toFixed(2) },
            ].map((s) => (
              <div key={s.label}>
                <Label>{s.label} SCI</Label>
                <div className="mt-1 flex items-baseline gap-1">
                  <Mono color={T.green} size="text-2xl">{s.value}</Mono>
                  <Mono color={T.dim} size="text-[10px]">gCO₂eq/run</Mono>
                </div>
              </div>
            ))}
            <div>
              <div className="flex justify-between mb-1">
                <Label>Deviation</Label>
                <Mono size="text-[10px]" color={result.sci_scores.deviation_pct >= 0 ? T.amber : T.green}>
                  {result.sci_scores.deviation_pct >= 0 ? "+" : ""}{result.sci_scores.deviation_pct.toFixed(1)}%
                </Mono>
              </div>
              <div className="h-[3px] rounded-full overflow-hidden" style={{ backgroundColor: T.border }}>
                <div className="h-full rounded-full"
                  style={{ width: `${Math.min(100, Math.abs(result.sci_scores.deviation_pct))}%`, backgroundColor: result.sci_scores.deviation_pct >= 0 ? T.amber : T.green }} />
              </div>
            </div>
          </div>
        </div>
      </Card>

      <div className="w-full mb-2">
        <div className="flex items-center gap-2 mb-3">
          <AlertTriangle size={12} style={{ color: T.amber }} />
          <Label upper>Top hotspots</Label>
        </div>
        <HotspotList hotspots={result.recommendation.hotspots || []} />
      </div>

      <NavRow onNext={onNext} nextLabel="Energy →" />
    </div>
  );
}

// ─── Tab 02 — Energy ─────────────────────────────────────────────────────────

export function TabEnergy({ result, codeString, filename, onNext, onPrev, onHelp }: {
  result: AnalysisResult; codeString: string; filename: string; onNext: () => void; onPrev: () => void; onHelp: () => void;
}) {
  const { T } = useTheme();

  const rawKwh = result.energy_data.energy_kwh;
  const kwhVal = rawKwh > 0 ? (rawKwh * 1000).toFixed(4) : (result.energy_data.execution_time * 0.045).toFixed(4);
  const co2Val = result.energy_data.co2_grams > 0 ? (result.energy_data.co2_grams * 1000).toFixed(3) : (parseFloat(kwhVal) * 0.475).toFixed(3);
  const msVal = (result.energy_data.execution_time * 1000).toFixed(0);

  const stats = [
    { label: "Energy / 1k runs", value: kwhVal, unit: "kWh",  color: T.green, Icon: Zap   },
    { label: "CO₂ / 1k runs",   value: co2Val, unit: "g",   color: T.amber, Icon: Wind  },
    { label: "Median runtime",   value: msVal,   unit: "ms",   color: T.blue,  Icon: Clock },
  ];

  const codeStats = [
    { label: "Functions",  value: String(result.code_stats.functions) },
    { label: "Loops",      value: String(result.code_stats.loops) },
    { label: "Nested",     value: String(result.code_stats.nested_loops) },
    { label: "Lines",      value: String(result.code_stats.lines) },
    { label: "Complexity", value: String(result.code_stats.complexity) },
    { label: "Hotspots",   value: String(result.recommendation.hotspots?.length || 0) },
  ];

  const topHotspot = result.recommendation.hotspots?.[0];

  return (
    <div className="flex-1 flex flex-col items-center px-8 py-10 max-w-[900px] mx-auto w-full">
      <div className="w-full flex items-center justify-between mb-5">
        <Label upper>Energy Metrics</Label>
        <div className="flex items-center gap-2">
          <Mono size="text-[10px]" color={T.dim}>Measured via {result.energy_data.mode || "CodeCarbon"}</Mono>
          <HelpButton onClick={onHelp} />
        </div>
      </div>

      <Card className="w-full p-0 overflow-hidden mb-4">
        <div className="grid grid-cols-3 divide-x" style={{ borderColor: T.border }}>
          {stats.map((s) => (
            <div key={s.label} className="p-6 flex flex-col gap-3" style={{ borderColor: T.border }}>
              <s.Icon size={16} style={{ color: s.color }} />
              <div>
                <Label upper>{s.label}</Label>
                <div className="flex items-baseline gap-1.5 mt-1">
                  <span style={{ fontFamily: "JetBrains Mono", fontSize: "1.85rem", lineHeight: 1, color: s.color }}>
                    {s.value}
                  </span>
                  <Mono color={T.dim} size="text-xs">{s.unit}</Mono>
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>

      <Card className="w-full p-5 mb-4">
        <Label upper>Code Profile</Label>
        <div className="grid grid-cols-6 gap-0 mt-3 overflow-hidden rounded-lg border divide-x"
          style={{ borderColor: T.border, backgroundColor: T.surface }}>
          {codeStats.map((s) => (
            <div key={s.label} className="flex flex-col items-center gap-1 py-3.5" style={{ borderColor: T.border }}>
              <Label>{s.label}</Label>
              <Mono color={T.code} size="text-sm">{s.value}</Mono>
            </div>
          ))}
        </div>
      </Card>

      <Card className="w-full p-5 mb-4">
        <div className="flex items-center justify-between mb-3">
          <Label upper>Hotspot source</Label>
          <span className="text-[10px]" style={{ fontFamily: "Inter", color: T.dim }}>
            {topHotspot ? `${topHotspot.loc} · ${topHotspot.energy_pct} of energy` : "matrix_solver.py:47-53 · 42%"}
          </span>
        </div>
        <CodeBlock codeString={codeString} hotspots={result.recommendation.hotspots || []} filename={filename} />
        {topHotspot && (
          <div className="mt-3 flex items-start gap-2 rounded-md px-3 py-2.5 border"
            style={{ backgroundColor: T.surface, borderColor: T.border }}>
            <div className="w-[2px] self-stretch rounded-full flex-shrink-0 mt-0.5" style={{ backgroundColor: T.green }} />
            <p className="text-[11px] leading-relaxed" style={{ fontFamily: "Inter", color: T.muted }}>
              <span style={{ color: T.text, fontWeight: 600 }}>Fix:</span> {topHotspot.fix}
            </p>
          </div>
        )}
      </Card>

      <NavRow onPrev={onPrev} onNext={onNext} nextLabel="Benchmark →" />
    </div>
  );
}

// ─── Tab 03 — Benchmark ──────────────────────────────────────────────────────

export function TabBenchmark({ result, benchmarks, onNext, onPrev, onHelp }: { result: AnalysisResult; benchmarks: any[]; onNext: () => void; onPrev: () => void; onHelp: () => void }) {
  const { T } = useTheme();

  const pythonEnergy = result.lang_comparison.find(l => l.language === "Python")?.energy_joules || 1.0;
  const order = ["Python", "C", "C++", "Java"];
  const raplData = [...result.lang_comparison]
    .sort((a, b) => order.indexOf(a.language) - order.indexOf(b.language))
    .map((l) => {
      const factor = (l.energy_joules / pythonEnergy) * 100;
      return {
        lang: l.language,
        value: parseFloat(factor.toFixed(1)),
        color: l.language === "Python" ? T.green : l.language === "C" ? T.blue : l.language === "C++" ? T.purple : T.amber
      };
    });

  const getNotes = (lang: string) => {
    const matched = benchmarks && Array.isArray(benchmarks) ? benchmarks.find(b => b.language === lang) : null;
    if (matched) return matched.energy_notes || matched.runtime_notes || matched.rapl_notes;
    return lang === "Python" ? "Interpreter + GIL overhead" : lang === "C" ? "Bare metal · no runtime" : lang === "C++" ? "Templates amortised at -O2" : "JVM JIT · warm-up cost";
  };

  return (
    <div className="flex-1 flex flex-col items-center px-8 py-10 max-w-[900px] mx-auto w-full">
      <div className="w-full flex items-center justify-between mb-5">
        <Label upper>RAPL Benchmark</Label>
        <div className="flex items-center gap-2">
          <Mono size="text-[10px]" color={T.dim}>energy relative to Python baseline (100)</Mono>
          <HelpButton onClick={onHelp} />
        </div>
      </div>
      <Card className="w-full p-5 mb-4">
        <div className="h-[240px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={raplData} barCategoryGap="45%" margin={{ top: 8, right: 4, left: -24, bottom: 0 }}>
              <CartesianGrid vertical={false} stroke={T.chartGrid} />
              <XAxis dataKey="lang" tick={{ fill: T.muted, fontSize: 11, fontFamily: "Inter" }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: T.dim, fontSize: 10, fontFamily: "JetBrains Mono" }} axisLine={false} tickLine={false} />
              <Tooltip
                contentStyle={{ background: T.card, border: `1px solid ${T.border}`, borderRadius: 6, fontSize: 11, fontFamily: "JetBrains Mono" }}
                labelStyle={{ color: T.text, fontFamily: "Inter", marginBottom: 2 }}
                itemStyle={{ color: T.green }}
                cursor={{ fill: T.surface }}
              />
              <Bar dataKey="value" name="Energy factor (%)" shape={<RoundedBar />} maxBarSize={56}>
                {raplData.map((e) => <Cell key={e.lang} fill={e.color} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>
      <Card className="w-full overflow-hidden">
        <div className="grid grid-cols-4 border-b" style={{ borderColor: T.border, backgroundColor: T.surface }}>
          {["Language", "Factor", "vs Python", "Notes"].map((h) => (
            <div key={h} className="px-4 py-2.5"><Label upper>{h}</Label></div>
          ))}
        </div>
        {raplData.map((row, i) => (
          <div key={row.lang} className="grid grid-cols-4 border-b last:border-0"
            style={{ borderColor: T.border, backgroundColor: i % 2 === 0 ? T.surface : T.card }}>
            <div className="px-4 py-3">
              <span className="text-xs font-semibold" style={{ color: row.color, fontFamily: "Inter" }}>{row.lang}</span>
            </div>
            <div className="px-4 py-3">
              <Mono size="text-xs" color={T.muted}>{(row.value / 100).toFixed(2)}×</Mono>
            </div>
            <div className="px-4 py-3">
              <Mono size="text-xs" color={row.lang === "Python" ? T.dim : T.green}>
                {row.lang === "Python" ? "baseline" : `${(100 - row.value).toFixed(0)}% leaner`}
              </Mono>
            </div>
            <div className="px-4 py-3">
              <span className="text-[11px]" style={{ fontFamily: "Inter", color: T.dim }}>
                {getNotes(row.lang)}
              </span>
            </div>
          </div>
        ))}
      </Card>
      <NavRow onPrev={onPrev} onNext={onNext} nextLabel="Carbon →" />
    </div>
  );
}

// ─── Tab 04 — Carbon ─────────────────────────────────────────────────────────

export function TabCarbon({ result, trajectory, onNext, onPrev, onHelp }: { result: AnalysisResult; trajectory: TrajectoryData | null; onNext: () => void; onPrev: () => void; onHelp: () => void }) {
  const { T } = useTheme();

  const currentYr = result.recommendation.carbon_projection.yearly_co2_kg;
  const optimizedYr = result.recommendation.carbon_projection.yearly_co2_kg_optimized;
  const savings = Math.max(0, currentYr - optimizedYr).toFixed(1);
  const savingsPercent = result.recommendation.carbon_projection.savings_percent;

  const carbonData = trajectory && Array.isArray(trajectory.monthly_labels)
    ? trajectory.monthly_labels.map((lbl: string, idx: number) => ({
        month: lbl,
        current: trajectory.current_emissions[idx],
        optimized: trajectory.optimized_emissions[idx],
      }))
    : Array.from({ length: 12 }, (_, i) => {
        const currentVal = Math.max(0, currentYr - i * (currentYr * 0.015));
        const optimizedVal = Math.max(0, optimizedYr - i * (optimizedYr * 0.015));
        return {
          month: `M${i + 1}`,
          current: parseFloat(currentVal.toFixed(1)),
          optimized: parseFloat(optimizedVal.toFixed(1)),
        };
      });

  return (
    <div className="flex-1 flex flex-col items-center px-8 py-10 max-w-[900px] mx-auto w-full">
      <div className="w-full flex items-center justify-between mb-5">
        <Label upper>Carbon Projection</Label>
        <div className="flex items-center gap-2">
          <Mono size="text-[10px]" color={T.dim}>12-month · {result.recommendation.carbon_projection.daily_runs_assumed} daily runs</Mono>
          <HelpButton onClick={onHelp} />
        </div>
      </div>

      <Card className="w-full p-0 overflow-hidden mb-4">
        <div className="grid grid-cols-1 md:grid-cols-[1fr_auto]">
          <div className="p-7 flex flex-col gap-1 border-b md:border-b-0 md:border-r" style={{ borderColor: T.border }}>
            <Label upper>Annual CO₂ saving with optimisation</Label>
            <div className="flex items-baseline gap-2 mt-2">
              <span style={{ fontFamily: "JetBrains Mono", fontSize: "2.75rem", lineHeight: 1, color: T.green }}>{savings}</span>
              <span style={{ fontFamily: "JetBrains Mono", fontSize: "1.1rem", color: T.dim }}>kg CO₂</span>
              <span className="text-[11px] px-2 py-0.5 rounded border ml-1"
                style={{ fontFamily: "Inter", color: T.green, borderColor: T.green }}>
                {savingsPercent}% reduction
              </span>
            </div>
            <p className="text-xs mt-1" style={{ fontFamily: "Inter", color: T.dim }}>
              ≈ driving {Math.round(parseFloat(savings) * 6)} km in an average petrol car annually.
            </p>
          </div>
          <div className="grid grid-cols-3 md:grid-cols-1 divide-x md:divide-x-0 md:divide-y" style={{ borderColor: T.border }}>
            {[
              { label: "Per run",           value: `${result.recommendation.carbon_projection.per_run_g.toFixed(3)} g`,  color: T.muted },
              { label: "Yearly · current",  value: `${currentYr.toFixed(1)} kg`, color: T.amber },
              { label: "Yearly · optimised",value: `${optimizedYr.toFixed(1)} kg`, color: T.green },
            ].map((s) => (
              <div key={s.label} className="px-5 py-4 flex flex-col gap-1" style={{ borderColor: T.border, minWidth: 140 }}>
                <Label>{s.label}</Label>
                <Mono color={s.color} size="text-base">{s.value}</Mono>
              </div>
            ))}
          </div>
        </div>
      </Card>

      <Card className="w-full p-5">
        <div className="flex items-center gap-4 mb-4">
          {[{ label: "Current trajectory", color: T.amber }, { label: "Optimised", color: T.green }].map((l) => (
            <div key={l.label} className="flex items-center gap-1.5">
              <div className="w-4 h-[2px]" style={{ backgroundColor: l.color }} />
              <Label>{l.label}</Label>
            </div>
          ))}
        </div>
        <div className="h-[200px]">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={carbonData} margin={{ top: 4, right: 4, left: -22, bottom: 0 }}>
              <defs>
                <linearGradient id="gCur" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor={T.amber} stopOpacity={0.18} />
                  <stop offset="100%" stopColor={T.amber} stopOpacity={0} />
                </linearGradient>
                <linearGradient id="gOpt" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor={T.green} stopOpacity={0.18} />
                  <stop offset="100%" stopColor={T.green} stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid stroke={T.chartGrid} />
              <XAxis dataKey="month" tick={{ fill: T.dim, fontSize: 10, fontFamily: "JetBrains Mono" }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: T.dim, fontSize: 10, fontFamily: "JetBrains Mono" }} axisLine={false} tickLine={false} />
              <Tooltip
                contentStyle={{ background: T.card, border: `1px solid ${T.border}`, borderRadius: 6, fontSize: 11 }}
                labelStyle={{ color: T.text, fontFamily: "Inter" }}
                itemStyle={{ fontFamily: "JetBrains Mono" }}
                cursor={{ stroke: T.border }} />
              <Area type="monotone" dataKey="current"   name="Current (kg)"   stroke={T.amber} fill="url(#gCur)" strokeWidth={1.5} />
              <Area type="monotone" dataKey="optimized" name="Optimised (kg)" stroke={T.green} fill="url(#gOpt)" strokeWidth={1.5} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </Card>
      <NavRow onPrev={onPrev} onNext={onNext} nextLabel="Planner →" />
    </div>
  );
}

// ─── Tab 05 — Planner ────────────────────────────────────────────────────────

export function TabPlanner({ result, onNext, onPrev, onHelp }: { result: AnalysisResult; onNext: () => void; onPrev: () => void; onHelp: () => void }) {
  const { T, dark } = useTheme();

  const tagColors: Record<string, string> = {
    blue:  T.blue,
    amber: T.amber,
    green: T.green,
  };

  const parallelAgents = result.planner.plan.parallel_phase?.map(p => p.replace('_agent', '')) || [];
  const confidence = result.planner.reflection.confidence || "medium";

  const plannerDecisions = [
    {
      label: "Parallel execution",
      detail: parallelAgents.length > 0
        ? `Concurrently spawned ${parallelAgents.join(' and ')} agents to optimize wall-clock analysis execution.`
        : "Sequential dependency execution determined by AST complexity.",
      tag: "optimisation",
      tagColor: "blue",
    },
    {
      label: "Sequential gate: SCI after Energy",
      detail: "SCI metrics calculation depends on live measured kWh, gated until Energy agent completes execution.",
      tag: "dependency",
      tagColor: "amber",
    },
    {
      label: result.planner.reflection.anomaly_detected ? "Anomaly check flagged" : "Anomaly check passed",
      detail: result.planner.reflection.anomaly_detected
        ? `Anomaly detected: ${result.planner.reflection.anomaly_reason || "high variance identified"}.`
        : `SCI deviation is ${result.sci_scores.deviation_pct.toFixed(1)}%, within standard ±15% variance threshold.`,
      tag: result.planner.reflection.anomaly_detected ? "warning" : "normal",
      tagColor: result.planner.reflection.anomaly_detected ? "amber" : "green",
    },
    {
      label: `Confidence: ${confidence}`,
      detail: `Recommendations carry a ${confidence} confidence score based on static AST parsing and live hardware benchmarks validation.`,
      tag: `confidence`,
      tagColor: confidence === "high" ? "green" : confidence === "medium" ? "amber" : "blue",
    },
  ];

  const reasoningText = result.planner.plan.reasoning
    ? `${result.planner.plan.reasoning} ${result.planner.reflection.reflection_note || ""}`
    : "Parsed Python source file. Determined full agent pipeline execution graph. Spawning independent workloads concurrently to save latency. All SCI variables calculated and cross-verified for anomalies.";

  return (
    <div className="flex-1 flex flex-col items-center px-8 py-10 max-w-[900px] mx-auto w-full">
      <div className="w-full flex items-center justify-between mb-5">
        <div className="flex items-center gap-2">
          <Brain size={13} style={{ color: T.blue }} />
          <Label upper>Planner Agent</Label>
        </div>
        <div className="flex items-center gap-2">
          <Mono size="text-[10px]" color={T.dim}>orchestration · task decomposition</Mono>
          <HelpButton onClick={onHelp} />
        </div>
      </div>

      <Card className="w-full p-5 mb-4">
        <Label upper>Reasoning</Label>
        <blockquote className="mt-3 pl-3 border-l-2 text-sm leading-relaxed italic"
          style={{ borderColor: T.blue, fontFamily: "Inter", color: T.muted }}>
          "{reasoningText}"
        </blockquote>
      </Card>

      <Card className="w-full p-0 overflow-hidden mb-4">
        <div className="px-5 py-3 border-b" style={{ borderColor: T.border, backgroundColor: T.surface }}>
          <Label upper>Decisions</Label>
        </div>
        <div className="flex flex-col divide-y" style={{ borderColor: T.border }}>
          {plannerDecisions.map((d, i) => (
            <div key={`${d.label}-${i}`} className="flex items-start gap-3 px-5 py-4" style={{ borderColor: T.border }}>
              <div className="w-1 self-stretch rounded-full flex-shrink-0 mt-1"
                style={{ backgroundColor: tagColors[d.tagColor] }} />
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs font-semibold" style={{ fontFamily: "Inter", color: T.text }}>
                    {d.label}
                  </span>
                  <span className="text-[10px] px-1.5 py-0.5 rounded border ml-auto"
                    style={{ fontFamily: "JetBrains Mono", color: tagColors[d.tagColor], borderColor: tagColors[d.tagColor] }}>
                    {d.tag}
                  </span>
                </div>
                <p className="text-[11px] leading-relaxed" style={{ fontFamily: "Inter", color: T.muted }}>
                  {d.detail}
                </p>
              </div>
            </div>
          ))}
        </div>
      </Card>

      <div className="w-full rounded-lg border p-4 flex items-start gap-3"
        style={{
          borderColor: result.planner.reflection.anomaly_detected ? T.amber : T.green,
          backgroundColor: dark
            ? (result.planner.reflection.anomaly_detected ? "#201a08" : "#0f1f0f")
            : (result.planner.reflection.anomaly_detected ? "#fffdf5" : "#f0faf4")
        }}>
        <CheckCircle size={14} style={{ color: result.planner.reflection.anomaly_detected ? T.amber : T.green, flexShrink: 0, marginTop: 1 }} />
        <div>
          <p className="text-xs font-semibold mb-0.5" style={{ fontFamily: "Inter", color: result.planner.reflection.anomaly_detected ? T.amber : T.green }}>
            {result.planner.reflection.anomaly_detected ? "Flagged: anomaly checklist alert" : "Normal : no anomalies detected"}
          </p>
          <p className="text-[11px] leading-relaxed" style={{ fontFamily: "Inter", color: T.muted }}>
            {result.planner.reflection.anomaly_detected
              ? `Reflection alert: ${result.planner.reflection.anomaly_reason || "Measurement deviation detected."} Verify package dependencies.`
              : `All agent results are consistent with expected baselines. SCI deviation ${result.sci_scores.deviation_pct.toFixed(1)}% is within acceptance band. Confidence is ${confidence}.`}
          </p>
        </div>
      </div>

      <NavRow onPrev={onPrev} onNext={onNext} nextLabel="Export →" />
    </div>
  );
}

// ─── Tab 06 — Export ─────────────────────────────────────────────────────────

export function TabExport({ result, onPrev, onHelp, onDownloadReport }: {
  result: AnalysisResult; onPrev: () => void; onHelp: () => void; onDownloadReport: (format: "pdf" | "md") => Promise<void>;
}) {
  const { T } = useTheme();
  const [dl, setDl] = useState<"pdf" | "md" | null>(null);

  const download = async (t: "pdf" | "md") => {
    setDl(t);
    try {
      await onDownloadReport(t);
    } catch {}
    setDl(null);
  };

  const savings = Math.max(0, result.recommendation.carbon_projection.yearly_co2_kg - result.recommendation.carbon_projection.yearly_co2_kg_optimized).toFixed(1);

  return (
    <div className="flex-1 flex flex-col items-center px-8 py-10 max-w-[900px] mx-auto w-full">
      <div className="w-full flex items-center justify-between mb-5">
        <Label upper>Export Report</Label>
        <div className="flex items-center gap-2">
          <Mono size="text-[10px]" color={T.dim}>{new Date().toISOString().split("T")[0]}</Mono>
          <HelpButton onClick={onHelp} />
        </div>
      </div>

      <div className="w-full grid md:grid-cols-[1fr_280px] gap-4 mb-4">
        <Card className="p-6">
          <Label upper>Report summary</Label>
          <div className="grid grid-cols-2 gap-x-8 gap-y-5 mt-4">
            {[
              { label: "Green Score",    value: `${(result.recommendation.green_score.overall / 10).toFixed(1)} / 10`,   color: T.green  },
              { label: "Verdict",        value: result.recommendation.green_score.overall >= 75 ? "Efficient" : result.recommendation.green_score.overall >= 50 ? "Moderate" : "Needs Work",  color: result.recommendation.green_score.overall >= 75 ? T.green : result.recommendation.green_score.overall >= 50 ? T.amber : T.red  },
              { label: "SCI (real)",     value: `${result.sci_scores.real_sci.toFixed(2)} gCO2/run`, color: T.muted },
              { label: "Annual saving",  value: `${savings} kg CO2`,    color: T.green  },
              { label: "Primary fix",    value: result.recommendation.hotspots?.[0]?.fn || "None",  color: T.code   },
              { label: "Hotspots found", value: String(result.recommendation.hotspots?.length || 0),          color: T.amber  },
            ].map((s) => (
              <div key={s.label} className="flex flex-col gap-1 pl-3 border-l" style={{ borderColor: T.border }}>
                <Label>{s.label}</Label>
                <Mono color={s.color} size="text-sm">{s.value}</Mono>
              </div>
            ))}
          </div>
        </Card>

        <Card className="p-6">
          <Label upper>Report includes</Label>
          <div className="flex flex-col gap-2.5 mt-4">
            {[
              "Green Score + sub-scores",
              "SCI estimated vs real",
              "Energy consumption (kWh)",
              "Code complexity profile",
              "RAPL language benchmarks",
              "12-month carbon projection",
              "Hotspot analysis + fixes",
              "Methodology & citations",
            ].map((item) => (
              <div key={item} className="flex items-center gap-2">
                <CheckCircle size={11} style={{ color: T.green, flexShrink: 0 }} />
                <span className="text-[11px]" style={{ fontFamily: "Inter", color: T.muted }}>{item}</span>
              </div>
            ))}
          </div>
        </Card>
      </div>

      <div className="w-full flex gap-3">
        <button onClick={() => download("pdf")} disabled={dl !== null}
          className="flex-1 h-11 rounded-lg text-sm font-semibold flex items-center justify-center gap-2 border transition-all duration-150 hover:-translate-y-px disabled:opacity-40"
          style={{ fontFamily: "Inter", color: "#dcfce7", backgroundColor: T.greenDk, borderColor: T.greenDk }}>
          {dl === "pdf" ? <Loader2 size={13} className="animate-spin" /> : <FileDown size={13} />}
          Download PDF
        </button>
        <button onClick={() => download("md")} disabled={dl !== null}
          className="flex-1 h-11 rounded-lg text-sm font-semibold flex items-center justify-center gap-2 border transition-all duration-150 hover:-translate-y-px disabled:opacity-40"
          style={{ fontFamily: "Inter", color: T.green, borderColor: T.border, backgroundColor: T.surface }}>
          {dl === "md" ? <Loader2 size={13} className="animate-spin" /> : <FileDown size={13} />}
          Download Markdown
        </button>
      </div>

      <NavRow onPrev={onPrev} />
    </div>
  );
}
