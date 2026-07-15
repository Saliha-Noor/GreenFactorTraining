import React, { useState, useEffect } from "react";
import {
  HelpCircle, X, ChevronDown, ArrowUpRight, CheckCircle,
  FileCode, UserCircle, Bell, EyeOff, Eye, Copy, Key, LogIn, Trash2
} from "lucide-react";
import { useTheme } from "../theme";
import { Label, Mono } from "../components/ui";
import { revokeApiKey, generateApiKey, deleteAccount } from "../../utils/api";
import type { UserSettings } from "../../utils/api";

function formatSignupDate(d: string): string {
  if (!d) return 'Today';
  const date = new Date(d);
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  return `${months[date.getMonth()]} ${date.getFullYear()}`;
}

// ─── Help Drawer / Panel ──────────────────────────────────────────────────────

interface HelpSection {
  heading: string;
  body: string;
}

interface HelpFaq {
  q: string;
  a: string;
}

export function HelpPanel({ tabIndex, helpArticles, faqs, onClose }: {
  tabIndex: number;
  helpArticles: any;
  faqs: any;
  onClose: () => void;
}) {
  const { T, dark } = useTheme();
  const [visible, setVisible] = useState(false);
  const [openFaq, setOpenFaq] = useState<number | null>(null);

  const articleCategory = helpArticles && Array.isArray(helpArticles)
    ? helpArticles.find((c: any) => c.category_index === tabIndex)
    : null;

  const content = articleCategory ? {
    title: articleCategory.title,
    intro: articleCategory.intro,
    sections: articleCategory.sections.map((s: any) => ({ heading: s.heading, body: s.body })) as HelpSection[]
  } : {
    title: "Loading...",
    intro: "",
    sections: [] as HelpSection[]
  };

  const matchedFaqs = faqs && Array.isArray(faqs)
    ? faqs.filter((f: any) => f.category_index === tabIndex).map((f: any) => ({ q: f.question, a: f.answer }))
    : ([] as HelpFaq[]);

  useEffect(() => {
    const id = requestAnimationFrame(() => setVisible(true));
    return () => cancelAnimationFrame(id);
  }, []);

  const close = () => {
    setVisible(false);
    setTimeout(onClose, 300);
  };

  return (
    <>
      <div
        className="fixed inset-0 z-[90] transition-opacity duration-300"
        style={{ backgroundColor: "rgba(0,0,0,0.5)", opacity: visible ? 1 : 0 }}
        onClick={close}
      />

      <div
        className="fixed top-0 right-0 bottom-0 z-[95] flex flex-col overflow-y-auto transition-transform duration-300 ease-[cubic-bezier(0.4,0,0.2,1)]"
        style={{
          width: "25vw", minWidth: 320,
          backgroundColor: T.bg,
          borderLeft: `1px solid ${T.border}`,
          transform: visible ? "translateX(0)" : "translateX(100%)",
          scrollbarWidth: "none",
          boxShadow: dark ? "-12px 0 40px rgba(0,0,0,0.6)" : "-12px 0 40px rgba(0,0,0,0.12)",
        }}
      >
        <div className="sticky top-0 z-10 flex items-center justify-between px-6 h-14 border-b flex-shrink-0"
          style={{ backgroundColor: T.bg, borderColor: T.border }}>
          <div className="flex items-center gap-2">
            <HelpCircle size={14} style={{ color: T.green }} />
            <span style={{ fontFamily: "Inter", fontWeight: 700, fontSize: 13, color: T.text }}>
              Help — {content.title}
            </span>
          </div>
          <button onClick={close}
            className="w-7 h-7 rounded-md flex items-center justify-center border transition-colors"
            style={{ borderColor: T.border, backgroundColor: T.surface, color: T.dim }}>
            <X size={12} />
          </button>
        </div>

        <div className="px-6 py-5 border-b" style={{ borderColor: T.border, backgroundColor: T.surface }}>
          <p className="text-[12px] leading-relaxed" style={{ fontFamily: "Inter", color: T.muted }}>
            {content.intro}
          </p>
        </div>

        <div className="px-6 py-5 border-b" style={{ borderColor: T.border }}>
          <div className="flex items-center gap-2 mb-4">
            <div className="w-4 h-4 rounded flex items-center justify-center" style={{ backgroundColor: T.greenDk }}>
              <FileCode size={9} style={{ color: "#dcfce7" }} />
            </div>
            <span className="text-[10px] uppercase tracking-widest" style={{ fontFamily: "Inter", fontWeight: 700, color: T.dim }}>
              Documentation
            </span>
          </div>
          <div className="flex flex-col gap-5">
            {content.sections.map((s) => (
              <div key={s.heading}>
                <p className="text-[12px] mb-1.5" style={{ fontFamily: "Inter", fontWeight: 700, color: T.text }}>
                  {s.heading}
                </p>
                <p className="text-[11.5px] leading-relaxed" style={{ fontFamily: "Inter", color: T.muted }}>
                  {s.body}
                </p>
              </div>
            ))}
          </div>
        </div>

        <div className="px-6 py-5 border-b" style={{ borderColor: T.border }}>
          <div className="flex items-center gap-2 mb-4">
            <div className="w-4 h-4 rounded flex items-center justify-center" style={{ backgroundColor: T.greenDk }}>
              <HelpCircle size={9} style={{ color: "#dcfce7" }} />
            </div>
            <span className="text-[10px] uppercase tracking-widest" style={{ fontFamily: "Inter", fontWeight: 700, color: T.dim }}>
              FAQ
            </span>
          </div>
          <div className="flex flex-col gap-3">
            {matchedFaqs.map((faq: any, i: number) => (
              <div key={i} className="border rounded-lg overflow-hidden transition-colors"
                style={{ borderColor: T.border, backgroundColor: T.surface }}>
                <button
                  onClick={() => setOpenFaq(openFaq === i ? null : i)}
                  className="w-full flex items-center justify-between px-4 py-3 text-left transition-colors"
                  style={{ color: T.text }}
                >
                  <span className="text-[12px] font-semibold pr-4 leading-snug" style={{ fontFamily: "Inter" }}>
                    {faq.q}
                  </span>
                  <ChevronDown
                    size={12}
                    className="transition-transform duration-200 flex-shrink-0"
                    style={{
                      color: T.dim,
                      transform: openFaq === i ? "rotate(180deg)" : "rotate(0deg)"
                    }}
                  />
                </button>
                {openFaq === i && (
                  <div className="px-4 pb-3 pt-0 border-t" style={{ borderColor: T.border }}>
                    <p className="text-[11.5px] leading-relaxed m-0" style={{ fontFamily: "Inter", color: T.muted }}>
                      {faq.a}
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="h-8 flex-shrink-0" />
      </div>
    </>
  );
}

// ─── Profile Drawer / Panel ───────────────────────────────────────────────────

function PSection({ title, children }: { title: string; children: React.ReactNode }) {
  const { T } = useTheme();
  return (
    <div className="px-7 py-6 border-b" style={{ borderColor: T.border }}>
      <Label upper>{title}</Label>
      <div className="mt-4 flex flex-col gap-3">{children}</div>
    </div>
  );
}

interface PFieldProps { label: string; children: React.ReactNode }
function PField({ label, children }: PFieldProps) {
  const { T } = useTheme();
  return (
    <div className="flex flex-col gap-1.5">
      <label style={{ fontFamily: "Inter", fontSize: 11, fontWeight: 600, color: T.muted }}>{label}</label>
      {children}
    </div>
  );
}

function ProfileToggle({ on, onChange }: { on: boolean; onChange: () => void }) {
  const { T } = useTheme();
  return (
    <button type="button" onClick={onChange}
      className="w-9 h-5 rounded-full relative flex-shrink-0 transition-colors duration-200"
      style={{ backgroundColor: on ? T.green : T.border }}>
      <div className="absolute top-0.5 h-4 w-4 rounded-full transition-all duration-200"
        style={{ left: on ? "calc(100% - 18px)" : 2, backgroundColor: "#ffffff" }} />
    </button>
  );
}

export function ProfilePanel({
  onClose,
  settings,
  onUpdateSettings,
  onSignOut,
  history,
  analytics,
  apiKeys,
  billingPlan,
  onRefreshUserData,
}: {
  onClose: () => void;
  settings: UserSettings;
  onUpdateSettings: (s: Partial<UserSettings>) => void;
  onSignOut: () => void;
  history: any[];
  analytics: any;
  apiKeys: any[];
  billingPlan: any;
  onRefreshUserData: () => Promise<void>;
}) {
  const { T, dark } = useTheme();

  const [name, setName]         = useState(settings.name);
  const [email, setEmail]       = useState(settings.email);
  const [org, setOrg]           = useState(settings.org);
  const [region, setRegion]     = useState(settings.carbon_region || "Global");
  const [fmt, setFmt]           = useState(settings.report_format || "PDF");
  const [notifA, setNotifA]     = useState(settings.notify_analysis);

  const [focused, setFocus]     = useState<string | null>(null);
  const [saved, setSaved]       = useState(false);
  const [copied, setCopied]     = useState(false);

  const API_KEY = apiKeys && apiKeys.length > 0 ? apiKeys[0].key_string : "No API key generated";
  const maskedKey = API_KEY === "No API key generated"
    ? API_KEY
    : API_KEY.slice(0, 16) + "•".repeat(Math.max(0, API_KEY.length - 20)) + API_KEY.slice(-4);
  const [keyVis, setKeyVis]     = useState(false);

  const runs = analytics ? analytics.total_analyses : 0;
  const totalCo2 = history ? history.reduce((sum, h) => sum + (h.co2_grams || 0), 0) : 0;
  const totalSaved = history ? history.reduce((sum, h) => sum + (h.savings_kg || 0), 0) : 0;

  const co2Detected = totalCo2 >= 1000 ? `${(totalCo2 / 1000).toFixed(1)}kg` : `${totalCo2.toFixed(1)}g`;
  const co2Saved = totalSaved >= 1 ? `${totalSaved.toFixed(1)}kg` : `${(totalSaved * 1000).toFixed(0)}g`;

  const save = () => {
    onUpdateSettings({
      name,
      email,
      org,
      carbon_region: region,
      report_format: fmt,
      notify_analysis: notifA,
    });
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const copyKey = () => {
    if (API_KEY !== "No API key generated") {
      navigator.clipboard?.writeText(API_KEY);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const regenerateKey = async () => {
    try {
      if (apiKeys && apiKeys.length > 0) {
        await revokeApiKey(apiKeys[0].id);
      }
      await generateApiKey("Main API Key");
      await onRefreshUserData();
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (e) {
      console.error("Failed to regenerate API key:", e);
    }
  };

  const handleDeleteAccount = async () => {
    if (window.confirm("Are you sure you want to delete your account? This will permanently erase your profile, settings, history, and API keys. This action cannot be undone.")) {
      try {
        await deleteAccount();
        onSignOut();
      } catch (e) {
        alert("Failed to delete account: " + e);
      }
    }
  };

  const inputSt = (field: string): React.CSSProperties => ({
    width: "100%", height: 36, borderRadius: 8,
    border: `1px solid ${focused === field ? T.green : T.border}`,
    backgroundColor: T.surface, color: T.text,
    fontSize: 13, fontFamily: "Inter, sans-serif",
    padding: "0 12px", outline: "none", transition: "border-color 0.15s",
  });

  const selectSt: React.CSSProperties = {
    height: 36, borderRadius: 8,
    border: `1px solid ${T.border}`,
    backgroundColor: T.surface, color: T.text,
    fontSize: 13, fontFamily: "Inter, sans-serif",
    padding: "0 10px", outline: "none", cursor: "pointer",
  };

  const NOTIFS = [
    { label: "Analysis complete",    sub: "Notify when a run finishes",  on: notifA, set: () => setNotifA(!notifA) },
  ];

  const planName = billingPlan?.plan_type || "Local Plan";
  const planLimits = billingPlan?.limits === -1 ? "Unlimited local runs · no cloud quota" : `${billingPlan?.limits} runs monthly limit`;
  const planStatus = billingPlan?.status || "Active";

  return (
    <>
      <div className="fixed inset-0 z-50" style={{ backgroundColor: "rgba(0,0,0,0.45)", backdropFilter: "blur(2px)" }}
        onClick={onClose} />

      <div className="fixed top-0 right-0 bottom-0 z-50 flex flex-col w-full max-w-[460px] overflow-y-auto"
        style={{ backgroundColor: T.bg, borderLeft: `1px solid ${T.border}`, scrollbarWidth: "none" }}>

        <div className="sticky top-0 z-10 flex items-center justify-between px-7 h-14 border-b"
          style={{ backgroundColor: T.bg, borderColor: T.border, backdropFilter: "blur(12px)" }}>
          <div className="flex items-center gap-2.5">
            <UserCircle size={15} style={{ color: T.green }} />
            <span style={{ fontFamily: "Inter", fontWeight: 600, fontSize: 14, color: T.text }}>
              Profile &amp; Settings
            </span>
          </div>
          <button onClick={onClose}
            className="w-7 h-7 rounded-md flex items-center justify-center border transition-colors"
            style={{ borderColor: T.border, backgroundColor: T.surface, color: T.dim }}>
            <X size={12} />
          </button>
        </div>

        <div className="px-7 py-7 border-b flex items-center gap-5" style={{ borderColor: T.border, backgroundColor: T.surface }}>
          <div className="relative flex-shrink-0">
            <div className="w-16 h-16 rounded-2xl flex items-center justify-center"
               style={{ backgroundColor: T.greenDk }}>
              <span style={{ fontFamily: "Syne, sans-serif", fontWeight: 800, fontSize: "1.5rem", color: "#dcfce7" }}>
                {name ? name.split(" ").filter(Boolean).map(w => w[0]).join("").slice(0,2).toUpperCase() : "U"}
              </span>
            </div>
            <div className="absolute -bottom-1 -right-1 w-5 h-5 rounded-full flex items-center justify-center border-2"
              style={{ backgroundColor: T.green, borderColor: T.bg }}>
              <CheckCircle size={8} style={{ color: "#fff" }} />
            </div>
          </div>
          <div className="flex-1 min-w-0">
            <p style={{ fontFamily: "Syne, sans-serif", fontWeight: 800, fontSize: "1.1rem", color: T.text, lineHeight: 1.2 }}>
              {name || "Set your name"}
            </p>
            <p className="mt-1" style={{ fontFamily: "Inter", fontSize: 12, color: T.muted }}>
              {email || "Set your email"}
            </p>
            <div className="flex items-center gap-2 mt-2.5">
              <span className="text-[10px] px-2 py-0.5 rounded-full border"
                style={{ fontFamily: "Inter", color: T.green, borderColor: T.green }}>
                Developer
              </span>
              <span style={{ fontFamily: "Inter", fontSize: 10, color: T.dim }}>
                Member since {formatSignupDate(settings.created_at || "")}
              </span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-3 divide-x border-b" style={{ borderColor: T.border }}>
          {[
            { value: String(runs),       label: "Analyses run"  },
            { value: co2Detected,        label: "CO₂ detected"  },
            { value: co2Saved,           label: "CO₂ saved"     },
          ].map((s) => (
            <div key={s.label} className="flex flex-col items-center gap-0.5 py-4" style={{ borderColor: T.border }}>
              <span style={{ fontFamily: "Syne, sans-serif", fontWeight: 800, fontSize: "1rem", color: T.green }}>
                {s.value}
              </span>
              <span style={{ fontFamily: "Inter", fontSize: 10, color: T.dim }}>{s.label}</span>
            </div>
          ))}
        </div>

        <PSection title="Account Information">
          <PField label="Full name">
            <input type="text" value={name} onChange={(e) => setName(e.target.value)}
              onFocus={() => setFocus("name")} onBlur={() => setFocus(null)} style={inputSt("name")} />
          </PField>
          <PField label="Email address">
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)}
              onFocus={() => setFocus("email")} onBlur={() => setFocus(null)} style={inputSt("email")} />
          </PField>
          <PField label="Organisation">
            <input type="text" value={org} onChange={(e) => setOrg(e.target.value)}
              onFocus={() => setFocus("org")} onBlur={() => setFocus(null)} style={inputSt("org")} />
          </PField>
          <button onClick={save}
            className="self-start flex items-center gap-1.5 text-xs px-4 py-2 rounded-lg border transition-all duration-150 hover:-translate-y-px mt-1"
            style={{
              fontFamily: "Inter", fontWeight: 600,
              color: saved ? "#dcfce7" : T.green,
              backgroundColor: saved ? T.greenDk : "transparent",
              borderColor: saved ? T.greenDk : T.border,
            }}>
            {saved && <CheckCircle size={11} />}
            {saved ? "Saved" : "Save changes"}
          </button>
        </PSection>

        <PSection title="Preferences">
          <div className="grid grid-cols-2 gap-3">
            <PField label="Carbon region">
              <select value={region} onChange={(e) => setRegion(e.target.value)} style={selectSt}>
                {["Global", "EU", "US", "UK", "AU", "IN", "CN", "PK"].map((r) => <option key={r} value={r}>{r}</option>)}
              </select>
            </PField>
            <PField label="Report format">
              <select value={fmt} onChange={(e) => setFmt(e.target.value)} style={selectSt}>
                {["PDF", "Markdown", "JSON"].map((f) => <option key={f} value={f}>{f}</option>)}
              </select>
            </PField>
          </div>
          <div className="flex flex-col gap-0 mt-1 rounded-lg border overflow-hidden" style={{ borderColor: T.border }}>
            {NOTIFS.map((n, i) => (
              <div key={n.label}
                className={`flex items-center justify-between gap-4 px-4 py-3.5 ${i > 0 ? "border-t" : ""}`}
                style={{ borderColor: T.border, backgroundColor: T.surface }}>
                <div className="flex items-start gap-3">
                  <Bell size={13} style={{ color: T.dim, marginTop: 1, flexShrink: 0 }} />
                  <div>
                    <p style={{ fontFamily: "Inter", fontSize: 12, fontWeight: 600, color: T.text }}>{n.label}</p>
                    <p style={{ fontFamily: "Inter", fontSize: 11, color: T.dim }}>{n.sub}</p>
                  </div>
                </div>
                <ProfileToggle on={n.on} onChange={n.set} />
              </div>
            ))}
          </div>
        </PSection>

        <PSection title="API Access">
          <PField label="API key">
            <div className="flex items-center gap-2">
              <div className="flex-1 flex items-center h-9 rounded-lg border px-3 min-w-0"
                style={{ borderColor: T.border, backgroundColor: T.surface }}>
                <span className="truncate" style={{ fontFamily: "JetBrains Mono, monospace", fontSize: 11, color: T.dim }}>
                  {keyVis ? API_KEY : maskedKey}
                </span>
              </div>
              <button onClick={() => setKeyVis(!keyVis)}
                className="w-9 h-9 rounded-lg flex items-center justify-center border flex-shrink-0 transition-colors"
                style={{ borderColor: T.border, backgroundColor: T.surface, color: T.dim }}>
                {keyVis ? <EyeOff size={13} /> : <Eye size={13} />}
              </button>
              <button onClick={copyKey}
                className="w-9 h-9 rounded-lg flex items-center justify-center border flex-shrink-0 transition-colors"
                style={{ borderColor: copied ? T.green : T.border, backgroundColor: copied ? (dark ? "#0f1f0f" : "#f0faf4") : T.surface, color: copied ? T.green : T.dim }}>
                {copied ? <CheckCircle size={13} /> : <Copy size={13} />}
              </button>
            </div>
          </PField>
          <div className="flex items-center justify-between text-[11px] mt-1">
            <span style={{ fontFamily: "Inter", color: T.dim }}>{runs} requests total</span>
            <button onClick={regenerateKey}
              className="transition-colors" style={{ fontFamily: "Inter", color: T.blue }}>
              Regenerate
            </button>
          </div>

          <div className="flex items-center justify-between rounded-lg border px-4 py-3 mt-2"
            style={{ borderColor: T.border, backgroundColor: T.surface }}>
            <div className="flex items-center gap-3">
              <Key size={13} style={{ color: T.amber }} />
              <div>
                <p style={{ fontFamily: "Inter", fontSize: 12, fontWeight: 600, color: T.text }}>{planName}</p>
                <p style={{ fontFamily: "Inter", fontSize: 11, color: T.dim }}>{planLimits}</p>
              </div>
            </div>
            <span className="text-[10px] px-2 py-0.5 rounded-full border"
              style={{ fontFamily: "Inter", color: T.amber, borderColor: T.amber }}>
              {planStatus}
            </span>
          </div>
        </PSection>

        <PSection title="Danger Zone">
          <div className="flex flex-col gap-2">
            <button
              onClick={onSignOut}
              className="w-full h-9 rounded-lg text-[12px] flex items-center justify-center gap-2 border transition-all duration-150 hover:-translate-y-px"
              style={{ fontFamily: "Inter", fontWeight: 600, color: T.text, borderColor: T.border, backgroundColor: T.surface }}>
              <LogIn size={12} style={{ transform: "rotate(180deg)" }} />
              Sign out
            </button>
            <button
              onClick={handleDeleteAccount}
              className="w-full h-9 rounded-lg text-[12px] flex items-center justify-center gap-2 border transition-all duration-150 hover:-translate-y-px"
              style={{ fontFamily: "Inter", fontWeight: 600, color: T.red, borderColor: T.red, backgroundColor: "transparent" }}>
              <Trash2 size={12} />
              Delete account
            </button>
          </div>
        </PSection>

        <div className="h-8" />
      </div>
    </>
  );
}
