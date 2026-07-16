import { useState, useEffect, useCallback } from "react";
import {
  analyzeCode,
  downloadReport,
  downloadReportById,
  isAuthenticated,
  loadSettings,
  saveSettings,
  getAnalyticsUsage,
  getAnalyticsHistory,
  getAnalysisProjection,
  getHelpArticles,
  getFaqList,
  getBenchmarkNotes,
  getSampleScripts,
  listApiKeys,
  getBillingPlan,
  logout
} from "../utils/api";
import type {
  AnalysisResult,
  UserSettings,
  ApiKeyEntry,
  TrajectoryData
} from "../utils/api";
import { DARK, LIGHT, ThemeCtx } from "./theme";
import { Header, ResultsHUD, RESULT_TABS } from "./components/ui";
import { TabScore, TabEnergy, TabBenchmark, TabCarbon, TabPlanner, TabExport } from "./components/tabs";
import { HelpPanel, ProfilePanel } from "./screens/drawers";
import { LoginScreen, LandingScreen, LoadingScreen } from "./screens/auth_screens";
import { DUMMY_SCRIPTS } from "./components/constants";

type Screen = "login" | "landing" | "loading" | "results";

// ─── Results Screen ───────────────────────────────────────────────────────────

function ResultsScreen({
  filename,
  result,
  codeString,
  selectedFile,
  onDownloadReport,
  benchmarks,
  helpArticles,
  faqs,
}: {
  filename: string;
  result: AnalysisResult;
  codeString: string;
  selectedFile: File | null;
  onDownloadReport: (format: "pdf" | "md") => Promise<void>;
  benchmarks: any[];
  helpArticles: any;
  faqs: any;
}) {
  const [tab, setTab] = useState(0);
  const [helpOpen, setHelp] = useState(false);
  const [trajectory, setTrajectory] = useState<TrajectoryData | null>(null);
  const openHelp = () => setHelp(true);
  const closeHelp = () => setHelp(false);

  useEffect(() => {
    if (result && result.analysis_id) {
      getAnalysisProjection(result.analysis_id)
        .then(setTrajectory)
        .catch(console.error);
    } else {
      setTrajectory(null);
    }
  }, [result]);

  const handleKey = useCallback((e: KeyboardEvent) => {
    if (e.key === "Escape") { closeHelp(); return; }
    if (helpOpen) return;
    if (e.key === "ArrowRight") setTab((t) => Math.min(RESULT_TABS.length - 1, t + 1));
    if (e.key === "ArrowLeft") setTab((t) => Math.max(0, t - 1));
  }, [helpOpen]);

  useEffect(() => {
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [handleKey]);

  const next = () => setTab((t) => Math.min(RESULT_TABS.length - 1, t + 1));
  const prev = () => setTab((t) => Math.max(0, t - 1));

  return (
    <div className="flex-1 flex flex-col">
      <ResultsHUD active={tab} onSelect={setTab} />
      <div className="flex-1 overflow-y-auto" style={{ scrollbarWidth: "none" }}>
        {tab === 0 && <TabScore result={result} filename={filename} onNext={next} onHelp={openHelp} />}
        {tab === 1 && <TabEnergy result={result} codeString={codeString} filename={filename} onNext={next} onPrev={prev} onHelp={openHelp} />}
        {tab === 2 && <TabBenchmark result={result} benchmarks={benchmarks} onNext={next} onPrev={prev} onHelp={openHelp} />}
        {tab === 3 && <TabCarbon result={result} trajectory={trajectory} onNext={next} onPrev={prev} onHelp={openHelp} />}
        {tab === 4 && <TabPlanner result={result} onNext={next} onPrev={prev} onHelp={openHelp} />}
        {tab === 5 && <TabExport result={result} onPrev={prev} onHelp={openHelp} onDownloadReport={onDownloadReport} />}
      </div>
      {helpOpen && <HelpPanel tabIndex={tab} helpArticles={helpArticles} faqs={faqs} onClose={closeHelp} />}
    </div>
  );
}

// ─── App ──────────────────────────────────────────────────────────────────────

export default function App() {
  const [screen, setScreen] = useState<Screen>(() => isAuthenticated() ? "landing" : "login");
  const [filename, setFilename] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [codeString, setCodeString] = useState<string>("");
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [apiDone, setApiDone] = useState(false);
  const [animationDone, setAnimationDone] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const [dark, setDark] = useState(() => {
    try { const s = localStorage.getItem("greendev-theme"); if (s) return s === "dark"; } catch { }
    return window.matchMedia?.("(prefers-color-scheme: dark)").matches ?? true;
  });

  const [settings, setSettings] = useState<UserSettings>({
    name: "Developer",
    email: "",
    org: "",
    carbon_region: "Global",
    report_format: "PDF",
    notify_analysis: true,
    notify_updates: true,
    notify_marketing: false,
    notify_alerts: true,
  });

  const [helpArticles, setHelpArticles] = useState<any>(null);
  const [faqs, setFaqs] = useState<any>(null);
  const [benchmarks, setBenchmarks] = useState<any[]>([]);
  const [samples, setSamples] = useState<any[]>([]);
  const [history, setHistory] = useState<any[]>([]);
  const [analytics, setAnalytics] = useState<any>(null);
  const [apiKeys, setApiKeys] = useState<ApiKeyEntry[]>([]);
  const [billingPlan, setBillingPlan] = useState<any>(null);

  const refreshUserData = async () => {
    try {
      if (!isAuthenticated()) return;
      const [loadedSettings, userHistory, userAnalytics, keysList, planInfo] = await Promise.all([
        loadSettings(),
        getAnalyticsHistory(),
        getAnalyticsUsage(),
        listApiKeys(),
        getBillingPlan()
      ]);
      setSettings(loadedSettings);
      setHistory(userHistory);
      setAnalytics(userAnalytics);
      setApiKeys(keysList);
      setBillingPlan(planInfo);
    } catch (e) {
      console.error("Failed to load user data from backend:", e);
    }
  };

  const refreshCMSData = async () => {
    try {
      const [helpData, faqData, benchData, sampleData] = await Promise.all([
        getHelpArticles(),
        getFaqList(),
        getBenchmarkNotes(),
        getSampleScripts()
      ]);
      setHelpArticles(helpData);
      setFaqs(faqData);
      setBenchmarks(benchData);
      setSamples(sampleData);

      if (sampleData && sampleData.length > 0 && !filename) {
        setFilename(sampleData[0].filename);
        setCodeString(sampleData[0].source_code);
      }
    } catch (e) {
      console.error("Failed to load CMS data from backend:", e);
    }
  };

  useEffect(() => {
    refreshCMSData();
  }, []);

  useEffect(() => {
    if (isAuthenticated()) {
      refreshUserData();
      refreshCMSData();
    }
  }, [screen]);

  const toggle = () => setDark((d) => {
    const next = !d;
    try { localStorage.setItem("greendev-theme", next ? "dark" : "light"); } catch { }
    return next;
  });

  useEffect(() => {
    if (animationDone && apiDone && result) {
      setScreen("results");
    }
  }, [animationDone, apiDone, result]);

  const handleLogin = () => {
    refreshUserData().then(() => {
      setScreen("landing");
    });
  };

  const handleSignOut = () => {
    logout();
    setProfileOpen(false);
    setScreen("login");
    setHistory([]);
    setAnalytics(null);
    setApiKeys([]);
    setBillingPlan(null);
  };

  useEffect(() => {
    const handleUnauthorized = () => {
      handleSignOut();
    };
    window.addEventListener("unauthorized", handleUnauthorized);
    return () => window.removeEventListener("unauthorized", handleUnauthorized);
  }, []);

  const handleUpdateSettings = async (newSettings: Partial<UserSettings>) => {
    const next = { ...settings, ...newSettings };
    setSettings(next);
    try {
      await saveSettings(next);
      await refreshUserData();
    } catch (e) {
      console.error("Failed to save settings to backend:", e);
    }
  };

  const handleAnalyze = async (fileObj: File) => {
    setFilename(fileObj.name);
    setSelectedFile(fileObj);
    setScreen("loading");
    setApiDone(false);
    setAnimationDone(false);
    setResult(null);

    const reader = new FileReader();
    reader.onload = (e) => {
      setCodeString(e.target?.result as string || "");
    };
    reader.readAsText(fileObj);

    try {
      const response = await analyzeCode(fileObj, settings.carbon_region);
      setResult(response);
      await refreshUserData();
      setApiDone(true);
    } catch (e) {
      console.error(e);
      alert("Analysis failed: " + (e instanceof Error ? e.message : String(e)));
      setScreen("landing");
    }
  };

  const handleSelectSample = (sampleName: string) => {
    const matched = samples && Array.isArray(samples) ? samples.find(s => s.filename === sampleName) : null;
    const code = matched ? matched.source_code : (DUMMY_SCRIPTS[sampleName] || DUMMY_SCRIPTS["matrix_solver.py"]);
    const fileObj = new File([code], sampleName, { type: "text/plain" });
    handleAnalyze(fileObj);
  };

  const handleDownloadReport = async (format: "pdf" | "md") => {
    if (result && result.analysis_id) {
      try {
        await downloadReportById(result.analysis_id, format);
        return;
      } catch (e) {
        console.error("Failed download by ID path, falling back to file upload", e);
      }
    }
    const matched = samples && Array.isArray(samples) ? samples.find(s => s.filename === filename) : null;
    const fallbackCode = DUMMY_SCRIPTS[filename] || DUMMY_SCRIPTS["matrix_solver.py"];
    const code = matched ? matched.source_code : codeString || fallbackCode;
    const activeFile = selectedFile || new File([code], filename || "matrix_solver.py", { type: "text/plain" });
    try {
      await downloadReport(activeFile, format);
    } catch (e) {
      console.error(e);
      alert("Failed to download report.");
    }
  };

  const T = dark ? DARK : LIGHT;

  return (
    <ThemeCtx.Provider value={{ T, dark, toggle }}>
      <div className="min-h-screen flex flex-col" style={{ backgroundColor: T.bg, transition: "background-color 0.2s" }}>
        {screen !== "login" && (
          <Header
            filename={screen === "results" ? filename : undefined}
            onProfileOpen={() => setProfileOpen(true)}
            settings={settings}
          />
        )}
        {profileOpen && (
          <ProfilePanel
            onClose={() => setProfileOpen(false)}
            settings={settings}
            onUpdateSettings={handleUpdateSettings}
            onSignOut={handleSignOut}
            history={history}
            analytics={analytics}
            apiKeys={apiKeys}
            billingPlan={billingPlan}
            onRefreshUserData={refreshUserData}
          />
        )}
        {screen === "login" && (
          <LoginScreen onLogin={handleLogin} />
        )}
        {screen === "landing" && (
          <LandingScreen
            samples={samples}
            onAnalyze={handleAnalyze}
            onSelectSample={handleSelectSample}
          />
        )}
        {screen === "loading" && (
          <LoadingScreen
            filename={filename}
            onAnimationDone={() => setAnimationDone(true)}
            apiDone={apiDone}
          />
        )}
        {screen === "results" && result && (
          <ResultsScreen
            filename={filename}
            result={result}
            codeString={codeString}
            selectedFile={selectedFile}
            onDownloadReport={handleDownloadReport}
            benchmarks={benchmarks}
            helpArticles={helpArticles}
            faqs={faqs}
          />
        )}
      </div>
    </ThemeCtx.Provider>
  );
}
