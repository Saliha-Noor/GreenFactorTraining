import React, { useState, useEffect, useRef } from "react";
import {
  Zap, BarChart2, Leaf, TrendingDown, AlertTriangle, LogIn,
  Sun, Moon, EyeOff, Eye, Shield, Loader2, CheckCircle, ArrowUpRight,
  FileCode, X, Upload
} from "lucide-react";
import { useTheme } from "../theme";
import { Label } from "../components/ui";
import { register, login } from "../../utils/api";
import type { SampleScript } from "../../utils/api";
import { AGENTS, LOG_LINES, PIPELINE_STEPS, DUMMY_SCRIPTS } from "../components/constants";
import type { AgentId } from "../components/constants";

// ─── Login Screen ─────────────────────────────────────────────────────────────

export function LoginScreen({ onLogin }: { onLogin: () => void }) {
  const { T, dark, toggle } = useTheme();
  const [email, setEmail]   = useState("");
  const [password, setPass] = useState("");
  const [name, setName]     = useState("");
  const [org, setOrg]       = useState("");
  const [isSignUp, setIsSignUp] = useState(false);
  const [showPw, setShowPw] = useState(false);
  const [focused, setFocus] = useState<"email" | "pass" | "name" | "org" | null>(null);
  const [busy, setBusy]     = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg("");
    setBusy(true);
    try {
      if (isSignUp) {
        await register(email, password, name, org);
      } else {
        await login(email, password);
      }
      onLogin();
    } catch (err: any) {
      setErrorMsg(err.message || "Authentication failed. Please check your credentials.");
    } finally {
      setBusy(false);
    }
  };

  const FEATURES = [
    { Icon: Zap,          text: "Energy profiling via RAPL hardware counters" },
    { Icon: BarChart2,    text: "Benchmark against C, C++ and Java baselines" },
    { Icon: Leaf,         text: "ISO 21031 Software Carbon Intensity scoring"  },
    { Icon: TrendingDown, text: "12-month carbon projection & reduction plan"  },
  ];

  const inputStyle = (field: "email" | "pass" | "name" | "org"): React.CSSProperties => ({
    width: "100%",
    height: 40,
    borderRadius: 8,
    border: `1px solid ${focused === field ? T.green : T.border}`,
    backgroundColor: T.surface,
    color: T.text,
    fontSize: 13,
    fontFamily: "Inter, sans-serif",
    padding: "0 12px",
    outline: "none",
    transition: "border-color 0.15s",
  });

  return (
    <div className="flex-1 flex" style={{ backgroundColor: T.bg }}>
      <div className="hidden lg:flex flex-col w-[500px] flex-shrink-0"
        style={{ backgroundColor: T.surface, borderRight: `1px solid ${T.border}` }}>

        <div className="flex items-center gap-2.5 p-10">
          <div className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0"
            style={{ backgroundColor: T.greenDk }}>
            <Leaf size={16} style={{ color: "#dcfce7" }} />
          </div>
          <span style={{ fontFamily: "Syne, sans-serif", fontWeight: 800, fontSize: "1.15rem", color: T.text }}>
            GreenDev<span style={{ color: T.green }}>AI</span>
          </span>
        </div>

        <div className="flex-1 flex flex-col justify-center px-10 pb-10">
          <h2 style={{
            fontFamily: "Syne, sans-serif", fontWeight: 800,
            fontSize: "clamp(1.8rem, 2.4vw, 2.3rem)", lineHeight: 1.14,
            color: T.text, marginBottom: 12,
          }}>
            Sustainable code<br />
            <span style={{ color: T.green }}>starts here.</span>
          </h2>
          <p className="text-sm leading-relaxed"
            style={{ fontFamily: "Inter", color: T.muted, maxWidth: 340, marginBottom: 28 }}>
            Upload a Python file. Five specialised agents + a planner run energy profiling, language
            benchmarking and SCI scoring — returning a Green Score with exact line-level fixes.
          </p>
          <div className="flex flex-col gap-3.5">
            {FEATURES.map((f) => (
              <div key={f.text} className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-md flex items-center justify-center flex-shrink-0 mt-px"
                  style={{ backgroundColor: T.greenDk }}>
                  <f.Icon size={11} style={{ color: "#dcfce7" }} />
                </div>
                <span className="text-[12px] leading-snug"
                  style={{ fontFamily: "Inter", color: T.muted }}>
                  {f.text}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="flex-1 flex flex-col min-w-0">
        <div className="flex items-center justify-between px-8 py-5">
          <div className="flex lg:hidden items-center gap-2">
            <div className="w-7 h-7 rounded-lg flex items-center justify-center"
              style={{ backgroundColor: T.greenDk }}>
              <Leaf size={12} style={{ color: "#dcfce7" }} />
            </div>
            <span style={{ fontFamily: "Syne, sans-serif", fontWeight: 800, fontSize: "0.95rem", color: T.text }}>
              GreenDev<span style={{ color: T.green }}>AI</span>
            </span>
          </div>
          <span className="hidden lg:block" />
          <button onClick={toggle}
            className="w-8 h-8 rounded-md flex items-center justify-center border transition-colors"
            style={{ borderColor: T.border, backgroundColor: T.surface, color: T.dim }}>
            {dark ? <Sun size={14} /> : <Moon size={14} />}
          </button>
        </div>

        <div className="flex-1 flex items-center justify-center px-8 pb-8">
          <div className="w-full max-w-[360px]">

            <div className="mb-7">
              <h1 style={{
                fontFamily: "Syne, sans-serif", fontWeight: 800,
                fontSize: "1.75rem", lineHeight: 1.2, color: T.text, marginBottom: 6,
              }}>
                {isSignUp ? "Create an account" : "Welcome back"}
              </h1>
              <p className="text-sm" style={{ fontFamily: "Inter", color: T.muted }}>
                {isSignUp ? "Sign up to start carbon scoring" : "Sign in to your GreenDev account"}
              </p>
            </div>

            {errorMsg && (
              <div className="mb-4 p-3 rounded-lg border text-xs leading-relaxed"
                style={{ borderColor: T.red, backgroundColor: "rgba(239,68,68,0.06)", color: T.red }}>
                <div className="flex gap-2">
                  <AlertTriangle size={14} className="shrink-0 mt-px" />
                  <span>{errorMsg}</span>
                </div>
              </div>
            )}

            <form onSubmit={submit} className="flex flex-col gap-4">

              {isSignUp && (
                <>
                  <div className="flex flex-col gap-1.5">
                    <label className="text-xs" style={{ fontFamily: "Inter", fontWeight: 600, color: T.muted }}>
                      Full name
                    </label>
                    <input
                      type="text"
                      value={name}
                      placeholder="Jane Doe"
                      onChange={(e) => setName(e.target.value)}
                      onFocus={() => setFocus("name")}
                      onBlur={() => setFocus(null)}
                      style={inputStyle("name")}
                      required
                    />
                  </div>

                  <div className="flex flex-col gap-1.5">
                    <label className="text-xs" style={{ fontFamily: "Inter", fontWeight: 600, color: T.muted }}>
                      Organisation
                    </label>
                    <input
                      type="text"
                      value={org}
                      placeholder="ACME Corp"
                      onChange={(e) => setOrg(e.target.value)}
                      onFocus={() => setFocus("org")}
                      onBlur={() => setFocus(null)}
                      style={inputStyle("org")}
                    />
                  </div>
                </>
              )}

              <div className="flex flex-col gap-1.5">
                <label className="text-xs" style={{ fontFamily: "Inter", fontWeight: 600, color: T.muted }}>
                  Email address
                </label>
                <input
                  type="email"
                  value={email}
                  placeholder="you@example.com"
                  onChange={(e) => setEmail(e.target.value)}
                  onFocus={() => setFocus("email")}
                  onBlur={() => setFocus(null)}
                  style={inputStyle("email")}
                  required
                />
              </div>

              <div className="flex flex-col gap-1.5">
                <div className="flex items-center justify-between">
                  <label className="text-xs" style={{ fontFamily: "Inter", fontWeight: 600, color: T.muted }}>
                    Password
                  </label>
                  {!isSignUp && (
                    <button type="button" className="text-[11px]"
                      style={{ fontFamily: "Inter", color: T.green }}>
                      Forgot password?
                    </button>
                  )}
                </div>
                <div className="relative">
                  <input
                    type={showPw ? "text" : "password"}
                    value={password}
                    placeholder="••••••••"
                    onChange={(e) => setPass(e.target.value)}
                    onFocus={() => setFocus("pass")}
                    onBlur={() => setFocus(null)}
                    style={{ ...inputStyle("pass"), paddingRight: 40 }}
                    required
                  />
                  <button type="button"
                    onClick={() => setShowPw(!showPw)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 transition-colors"
                    style={{ color: T.dim }}>
                    {showPw ? <EyeOff size={14} /> : <Eye size={14} />}
                  </button>
                </div>
              </div>

              <button type="submit" disabled={busy}
                className="w-full h-11 rounded-lg text-sm flex items-center justify-center gap-2 border transition-all duration-150 hover:-translate-y-px active:translate-y-0 disabled:opacity-60 mt-1"
                style={{ fontFamily: "Inter", fontWeight: 600, color: "#dcfce7", backgroundColor: T.greenDk, borderColor: T.greenDk }}>
                {busy ? <Loader2 size={14} className="animate-spin" /> : <LogIn size={14} />}
                {isSignUp ? "Sign up" : "Sign in"}
              </button>

            </form>

            <p className="text-center mt-6" style={{ fontFamily: "Inter", fontSize: 12, color: T.dim }}>
              {isSignUp ? "Already have an account?" : "Don't have an account?"}{" "}
              <button type="button" onClick={() => { setIsSignUp(!isSignUp); setErrorMsg(""); }}
                style={{ fontFamily: "Inter", color: T.green, fontWeight: 600 }}>
                {isSignUp ? "Sign in instead" : "Sign up for free"}
              </button>
            </p>

            <div className="flex items-center justify-center gap-1.5 mt-5">
              <Shield size={11} style={{ color: T.border }} />
              <span className="text-[10px]" style={{ fontFamily: "Inter", color: T.border }}>
                No data leaves your machine · open source
              </span>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
}

// ─── Landing — Mini Preview ───────────────────────────────────────────────────

function SamplePreview({ samples, onSelect }: { samples: SampleScript[]; onSelect: (name: string) => void }) {
  const { T } = useTheme();
  const r = 13, circ = 2 * Math.PI * r;

  const displaySamples = samples && samples.length > 0
    ? samples.map((s) => {
        const score = s.score || 75;
        const color = score >= 75 ? T.green : score >= 50 ? T.amber : T.red;
        const verdict = score >= 75 ? "Efficient" : score >= 50 ? "Moderate" : "Needs Work";
        return {
          file: s.filename,
          score: score,
          verdict: verdict,
          color: color
        };
      })
    : [
        { file: "matrix_solver.py",   score: 78, verdict: "Efficient", color: T.green },
        { file: "image_pipeline.py",  score: 54, verdict: "Moderate",  color: T.amber },
        { file: "data_loader.py",     score: 91, verdict: "Excellent", color: T.blue  },
      ];

  return (
    <div className="w-full rounded-lg border overflow-hidden mt-3" style={{ borderColor: T.border }}>
      <div className="px-3 py-2 border-b" style={{ borderColor: T.border, backgroundColor: T.surface }}>
        <Label upper>Sample outputs</Label>
      </div>
      {displaySamples.map((s) => (
        <div key={s.file}
          onClick={() => onSelect(s.file)}
          className="flex items-center gap-3 px-3 py-2.5 border-b last:border-0 cursor-pointer hover:bg-emerald-500/5 transition-all"
          style={{ borderColor: T.border }}>
          <svg width="36" height="36" viewBox="0 0 36 36" style={{ overflow: "visible" }}>
            <circle cx="18" cy="18" r={r} fill="none" stroke={T.border} strokeWidth="3" />
            <circle cx="18" cy="18" r={r} fill="none" stroke={s.color} strokeWidth="3"
              strokeLinecap="round"
              strokeDasharray={`${circ * (s.score / 100)} ${circ * (1 - s.score / 100)}`}
              transform="rotate(-90 18 18)" />
            <text x="18" y="18" textAnchor="middle" dominantBaseline="central" fill={T.text} fontSize="7.5" fontWeight="700" fontFamily="Syne, sans-serif">
              {(s.score / 10).toFixed(1)}
            </text>
          </svg>
          <div className="flex-1 min-w-0">
            <p className="text-xs truncate" style={{ fontFamily: "JetBrains Mono", color: T.text }}>{s.file}</p>
            <p className="text-[10px]" style={{ fontFamily: "Inter", color: s.color }}>{s.verdict}</p>
          </div>
          <ArrowUpRight size={12} style={{ color: T.dim, flexShrink: 0 }} />
        </div>
      ))}
    </div>
  );
}

// ─── Landing Screen ───────────────────────────────────────────────────────────

export function LandingScreen({ samples, onAnalyze, onSelectSample }: { samples: SampleScript[]; onAnalyze: (file: File) => void; onSelectSample: (name: string) => void }) {
  const { T } = useTheme();
  const [file, setFile]     = useState<File | null>(null);
  const [dragging, setDrag] = useState(false);
  const [error, setError]   = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  const accept = (f: File) => {
    if (!f.name.endsWith(".py")) {
      setError("Only .py files are supported.");
      return;
    }
    setError("");
    setFile(f);
  };

  return (
    <main className="flex-1 grid grid-cols-1 lg:grid-cols-2 w-full" style={{ minHeight: "calc(100vh - 56px)" }}>
      <div className="flex flex-col justify-center gap-9 px-10 py-16 lg:px-16 border-b lg:border-b-0 lg:border-r"
        style={{ borderColor: T.border }}>
        <div className="flex items-center gap-2">
          <span className="text-[10px] uppercase tracking-widest" style={{ fontFamily: "JetBrains Mono", color: T.dim }}>
            Python · Carbon Analysis
          </span>
        </div>

        <div>
          <h1 style={{ fontFamily: "Syne, sans-serif", fontWeight: 800,
            fontSize: "clamp(2.2rem, 4vw, 3.6rem)", lineHeight: 1.06, color: T.text }}>
            Measure the<br />
            <span style={{ color: T.green }}>carbon cost</span><br />
            of your code.
          </h1>
          <p className="text-sm leading-relaxed mt-4" style={{ fontFamily: "Inter", color: T.muted, maxWidth: 370 }}>
            Upload a Python file. Five specialised agents + a planner run energy profiling,
            language benchmarking, and SCI scoring, returning a Green Score with
            exact line-level fixes.
          </p>
        </div>

        <div className="rounded-xl border overflow-hidden" style={{ borderColor: T.border }}>
          {PIPELINE_STEPS.map((s) => (
            <div key={s.num}
              className="flex items-center gap-3.5 px-4 py-3 border-b last:border-0 transition-colors duration-100 group cursor-default"
              style={{ borderColor: T.border }}
              onMouseEnter={e => (e.currentTarget.style.backgroundColor = T.surface)}
              onMouseLeave={e => (e.currentTarget.style.backgroundColor = "transparent")}
            >
              <div className="w-1 h-1 rounded-full flex-shrink-0" style={{ backgroundColor: s.color }} />
              <span className="text-[10px] w-4 flex-shrink-0" style={{ fontFamily: "JetBrains Mono", color: T.border }}>
                {s.num}
              </span>
              <div className="flex-1 min-w-0">
                <span className="text-xs font-semibold" style={{ fontFamily: "Inter", color: T.text }}>{s.name}</span>
                <span className="text-[10px] ml-2" style={{ fontFamily: "Inter", color: T.dim }}>{s.detail}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="flex flex-col justify-center items-center px-10 py-16 lg:px-16">
        <div className="w-full max-w-[400px] flex flex-col gap-3">
          <div
            className="flex flex-col items-center justify-center gap-4 rounded-xl border-2 border-dashed cursor-pointer transition-colors duration-150"
            style={{
              minHeight: 220,
              borderColor: dragging ? T.green : error ? T.red : T.border,
              backgroundColor: dragging ? T.surface : T.card,
            }}
            onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
            onDragLeave={() => setDrag(false)}
            onDrop={(e) => { e.preventDefault(); setDrag(false); const f = e.dataTransfer.files[0]; if (f) accept(f); }}
            onClick={() => { if (!file) inputRef.current?.click(); }}
          >
            <input ref={inputRef} type="file" accept=".py" className="hidden"
              onChange={(e) => { const f = e.target.files?.[0]; if (f) accept(f); }} />

            {file ? (
              <div className="flex flex-col items-center gap-3 text-center px-6">
                <FileCode size={24} style={{ color: T.green }} />
                <div>
                  <p className="text-xs" style={{ fontFamily: "JetBrains Mono", color: T.text }}>{file.name}</p>
                  <p className="text-[11px] mt-0.5" style={{ fontFamily: "Inter", color: T.dim }}>
                    {(file.size / 1024).toFixed(1)} KB · Python
                  </p>
                </div>
                <button onClick={(e) => { e.stopPropagation(); setFile(null); setError(""); }}
                  className="flex items-center gap-1 text-[11px] px-2.5 py-1 rounded-md border transition-colors duration-100"
                  style={{ fontFamily: "Inter", color: T.dim, borderColor: T.border }}>
                  <X size={10} /> Remove
                </button>
              </div>
            ) : (
              <div className="flex flex-col items-center gap-2.5 text-center px-8">
                <div className="w-10 h-10 rounded-xl flex items-center justify-center"
                  style={{ backgroundColor: T.surface, border: `1px solid ${T.border}` }}>
                  <Upload size={18} style={{ color: T.dim }} />
                </div>
                <div>
                  <p className="text-sm" style={{ fontFamily: "Inter", color: T.muted }}>
                    Drop a <code style={{ fontFamily: "JetBrains Mono", color: T.green }}>.py</code> file here
                  </p>
                  <p className="text-xs mt-0.5" style={{ fontFamily: "Inter", color: T.dim }}>or click to browse</p>
                </div>
              </div>
            )}
          </div>

          {error && (
            <p className="text-[11px] text-center" style={{ fontFamily: "Inter", color: T.red }}>{error}</p>
          )}

          <button
            disabled={!file}
            onClick={() => {
              if (file) {
                onAnalyze(file);
              }
            }}
            className={`w-full h-11 rounded-lg text-sm font-semibold flex items-center justify-center gap-2 border transition-all duration-150 ${file ? "hover:-translate-y-px active:translate-y-0" : ""}`}
            style={{
              fontFamily: "Inter",
              color: file ? "#dcfce7" : T.dim,
              backgroundColor: file ? T.greenDk : T.surface,
              borderColor: file ? T.greenDk : T.border,
              opacity: file ? 1 : 0.6,
              cursor: file ? "pointer" : "not-allowed",
              boxShadow: file ? "0 1px 3px rgba(0,0,0,0.2)" : "none",
            }}>
            Analyze Code
          </button>

          <SamplePreview samples={samples} onSelect={onSelectSample} />
          <p className="text-center text-[10px] mt-0.5" style={{ fontFamily: "Inter", color: T.dim }}>
            Select a sample script below to run pre-loaded analysis
          </p>
        </div>
      </div>
    </main>
  );
}

// ─── Multi-agent DAG (loading) ────────────────────────────────────────────────

type AgentStatus = "idle" | "running" | "done";

function AgentNode({ label, sub, status, parallel = false }: {
  label: string; sub: string; status: AgentStatus; parallel?: boolean;
}) {
  const { T, dark } = useTheme();
  const isDone    = status === "done";
  const isRunning = status === "running";
  return (
    <div
      className="flex items-center gap-3 rounded-lg border px-3.5 py-2.5 transition-all duration-300"
      style={{
        borderColor: isDone || isRunning ? T.green : T.border,
        backgroundColor: isDone ? (!dark ? "#f0faf4" : "#0f1f0f") : T.surface,
        width: parallel ? 200 : 240,
        opacity: status === "idle" ? 0.45 : 1,
      }}
    >
      <div className="flex-shrink-0 w-5 h-5 flex items-center justify-center">
        {isDone    && <CheckCircle size={14} style={{ color: T.green }} />}
        {isRunning && <Loader2 size={14} className="animate-spin" style={{ color: T.green }} />}
        {!isDone && !isRunning && (
          <div className="w-3 h-3 rounded-full border-2" style={{ borderColor: T.border }} />
        )}
      </div>
      <div className="flex flex-col gap-0.5 min-w-0">
        <span className="text-xs font-semibold truncate"
          style={{ fontFamily: "Inter", color: isDone || isRunning ? T.text : T.dim }}>
          {label}
        </span>
        <span className="text-[10px] truncate"
          style={{ fontFamily: "JetBrains Mono", color: isDone ? T.green : T.dim }}>
          {sub}
        </span>
      </div>
    </div>
  );
}

function Connector() {
  const { T } = useTheme();
  return (
    <div className="flex justify-center my-1">
      <div className="w-px h-4" style={{ backgroundColor: T.border }} />
    </div>
  );
}

function AgentDAG({ onAnimationDone }: { onAnimationDone: () => void }) {
  const { T } = useTheme();
  const [statuses, setStatuses] = useState<Record<AgentId, AgentStatus>>(
    Object.fromEntries(AGENTS.map((a) => [a.id, "idle"])) as Record<AgentId, AgentStatus>
  );
  const [logs, setLogs] = useState<Array<{ id: string; msg: string; t: number }>>([]);
  const logRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const timers: ReturnType<typeof setTimeout>[] = [];
    AGENTS.forEach((a) => {
      timers.push(setTimeout(() => {
        setStatuses((s) => ({ ...s, [a.id]: "running" }));
      }, a.start));
      timers.push(setTimeout(() => {
        setStatuses((s) => ({ ...s, [a.id]: "done" }));
      }, a.end));
    });
    LOG_LINES.forEach((l) => {
      timers.push(setTimeout(() => {
        setLogs((prev) => [...prev, l]);
      }, l.t));
    });
    // Fire completion after 7.2 seconds
    timers.push(setTimeout(() => {
      onAnimationDone();
    }, 7200));

    return () => timers.forEach(clearTimeout);
  }, [onAnimationDone]);

  useEffect(() => {
    if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight;
  }, [logs]);

  const getStatus = (id: AgentId) => statuses[id] ?? "idle";

  const agentColor: Record<string, string> = {
    parse: T.blue, plan: T.purple, energy: T.green,
    bench: T.amber, sci: T.amber, rec: T.green, report: T.muted,
  };

  return (
    <div className="flex gap-8 items-start w-full max-w-[700px] mx-auto">
      <div className="flex flex-col items-center flex-shrink-0">
        <AgentNode label="Code Analysis" sub="ast.parse · McCabe complexity" status={getStatus("parse")} />
        <Connector />
        <AgentNode label="Planner" sub="task graph · dep resolution" status={getStatus("plan")} />
        <Connector />
        <div className="flex gap-3">
          <AgentNode label="Energy" sub="perf_event · RAPL counters" status={getStatus("energy")} parallel />
          <AgentNode label="Benchmark" sub="C · C++ · Java · baseline" status={getStatus("bench")} parallel />
        </div>
        <Connector />
        <AgentNode label="SCI" sub="ISO 21031 · carbon intensity" status={getStatus("sci")} />
        <Connector />
        <AgentNode label="Recommendation" sub="np.einsum · cache · generator" status={getStatus("rec")} />
        <Connector />
        <AgentNode label="Report Generator" sub="PDF · Markdown · JSON" status={getStatus("report")} />
      </div>

      <div className="flex-1 min-w-0 flex flex-col" style={{ minWidth: 0 }}>
        <div className="flex items-center justify-between mb-2">
          <Label upper>Live output</Label>
          <div className="flex items-center gap-1.5">
            <div className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ backgroundColor: T.green }} />
            <Label>running</Label>
          </div>
        </div>
        <div
          ref={logRef}
          className="flex-1 overflow-y-auto rounded-lg border p-3"
          style={{ borderColor: T.border, backgroundColor: T.surface, height: 320, scrollbarWidth: "none" }}
        >
          {logs.map((l, i) => (
            <div key={i} className="flex gap-2 mb-1.5 items-start">
              <span className="text-[10px] shrink-0" style={{ fontFamily: "JetBrains Mono", color: T.dim }}>
                {String(Math.floor(l.t / 1000)).padStart(2, "0")}:{String(l.t % 1000).padStart(3, "0")}
              </span>
              <span className="text-[10px] shrink-0 font-semibold"
                style={{ fontFamily: "JetBrains Mono", color: agentColor[l.id] ?? T.dim }}>
                [{l.id}]
              </span>
              <span className="text-[11px] break-all" style={{ fontFamily: "Inter", color: T.muted }}>{l.msg}</span>
            </div>
          ))}
          {logs.length === 0 && (
            <span className="text-[11px]" style={{ fontFamily: "Inter", color: T.border }}>Waiting for agents…</span>
          )}
        </div>
      </div>
    </div>
  );
}

// ─── Loading Screen ───────────────────────────────────────────────────────────

export function LoadingScreen({ filename, onAnimationDone, apiDone }: { filename: string; onAnimationDone: () => void; apiDone: boolean }) {
  const { T } = useTheme();

  return (
    <main className="flex-1 flex flex-col items-center justify-start px-8 pt-12 pb-8 gap-8">
      <div className="text-center">
        <p className="text-xs mb-1" style={{ fontFamily: "Inter", color: T.dim }}>
          Analysing
        </p>
        <p className="text-sm font-semibold" style={{ fontFamily: "JetBrains Mono", color: T.text }}>
          {filename}
        </p>
      </div>
      <AgentDAG onAnimationDone={onAnimationDone} />
      {!apiDone && (
        <p className="text-[11px] leading-relaxed animate-pulse mt-1" style={{ fontFamily: "Inter", color: T.green }}>
          Synchronizing hardware telemetry with carbon grid models...
        </p>
      )}
    </main>
  );
}
