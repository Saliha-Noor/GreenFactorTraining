// ─── API Types ────────────────────────────────────────────────────────────────

export interface CodeStats {
  functions: number;
  loops: number;
  nested_loops: number;
  classes: number;
  imports: number;
  comprehensions: number;
  recursion: boolean;
  lines: number;
  comment_lines: number;
  complexity: number;
  task_type: string;
}

export interface EnergyData {
  energy_kwh: number;
  co2_grams: number;
  execution_time: number;
  stdout: string;
  stderr: string;
  exec_error: string | null;
  mode: string;
}

export interface BenchmarkLang {
  energy_joules: number;
  time_seconds: number;
  memory_mb: number;
}

export interface BenchmarkData {
  python?: BenchmarkLang;
  c?: BenchmarkLang;
  cpp?: BenchmarkLang;
  java?: BenchmarkLang;
  task_type: string;
  source: string;
}

export interface LangComparison {
  language: string;
  energy_joules: number;
  time_seconds: number;
  memory_mb: number;
}

export interface SCIScores {
  estimated_sci: number;
  real_sci: number;
  deviation_pct: number;
  anomaly_detected: boolean;
  carbon_intensity: number;
  functional_unit: number;
}

export interface GreenScore {
  overall: number;
  performance: number;
  energy: number;
  carbon: number;
  maintainability: number;
}

export interface CarbonProjection {
  per_run_g: number;
  daily_runs_assumed: number;
  yearly_co2_kg: number;
  yearly_co2_kg_optimized: number;
  savings_percent: number;
}

export interface Hotspot {
  fn: string;
  loc: string;
  energy_pct: string;
  fix: string;
  severity: "high" | "medium" | "low";
}

export interface Recommendation {
  green_score: GreenScore;
  carbon_projection: CarbonProjection;
  hotspots?: Hotspot[];
  error?: string;
  raw?: string;
}

export interface PlannerData {
  plan: {
    plan: string[];
    parallel_phase: string[];
    skip_reason: Record<string, string | null>;
    reasoning: string;
  };
  reflection: {
    anomaly_detected: boolean;
    anomaly_reason: string | null;
    rerun_needed: boolean;
    reflection_note: string | null;
    confidence: string;
  };
}

export interface AnalysisResult {
  analysis_id?: number;
  filename: string;
  code_stats: CodeStats;
  energy_data: EnergyData;
  benchmark_data: BenchmarkData;
  lang_comparison: LangComparison[];
  sci_scores: SCIScores;
  recommendation: Recommendation;
  planner: PlannerData;
  timestamp: string;
}

export interface UserSettings {
  name: string;
  email: string;
  org: string;
  carbon_region: string;
  report_format: string;
  notify_analysis: boolean;
  notify_updates: boolean;
  notify_marketing: boolean;
  notify_alerts: boolean;
  created_at?: string;
}

export interface ApiKeyEntry {
  id: number;
  key_string: string;
  name: string;
  created_at: string;
  last_used_at: string | null;
  usage_count: number;
  is_active: number;
}

export interface BillingPlanInfo {
  plan_type: string;
  limits: number;
  status: string;
  expiration: string | null;
}

export interface BillingUsageInfo {
  requests_used: number;
  quota: number;
  billing_period: string;
}

export interface HistoryEntry {
  id: number;
  filename: string;
  score: number;
  co2_grams: number;
  savings_kg: number;
  timestamp: string;
}

export interface HelpSection {
  heading: string;
  body: string;
}

export interface HelpCategory {
  title: string;
  sections: HelpSection[];
}

export interface FaqItem {
  q: string;
  a: string;
}

export interface TutorialVideo {
  title: string;
  duration: string;
  url: string;
  thumbnail: string;
}

export interface LanguageBenchmarkNote {
  language: string;
  factor: number;
  energy_notes: string;
  runtime_notes: string;
  rapl_notes: string;
}

export interface SampleScript {
  filename: string;
  score: number;
  verdict: string;
  color: string;
  source_code: string;
}

export interface AnalyticsUsageInfo {
  total_requests: number;
  daily_requests: number;
  monthly_requests: number;
  last_request_timestamp: string | null;
  total_analyses: number;
  successful_analyses: number;
  failed_analyses: number;
  average_processing_time: number;
}

// ─── API Client Setup ─────────────────────────────────────────────────────────

const BASE = 'http://127.0.0.1:8000';
const TOKEN_KEY = 'greendev-token';

function getAuthHeaders(): Record<string, string> {
  const token = localStorage.getItem(TOKEN_KEY);
  return token ? { 'Authorization': `Bearer ${token}` } : {};
}

async function apiFetch(url: string, options: RequestInit = {}): Promise<any> {
  const headers = {
    ...getAuthHeaders(),
    ...(options.headers || {}),
  };

  const res = await fetch(`${BASE}${url}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    if (res.status === 401) {
      localStorage.removeItem(TOKEN_KEY);
      window.dispatchEvent(new Event("unauthorized"));
    }
    const err = await res.json().catch(() => ({ detail: 'Server error' }));
    throw new Error(err.detail || `Server error: ${res.status}`);
  }

  return res.json();
}

// ─── Authentication APIs ──────────────────────────────────────────────────────

export async function login(email: string, password: string): Promise<any> {
  const res = await fetch(`${BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Invalid credentials' }));
    throw new Error(err.detail || 'Login failed');
  }

  const data = await res.json();
  localStorage.setItem(TOKEN_KEY, data.token);
  return data.user;
}

export async function register(email: string, password: string, name: string, organization: string): Promise<any> {
  const res = await fetch(`${BASE}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, name, organization }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Registration failed' }));
    throw new Error(err.detail || 'Registration failed');
  }

  const data = await res.json();
  localStorage.setItem(TOKEN_KEY, data.token);
  return data.user;
}

export function isAuthenticated(): boolean {
  return !!localStorage.getItem(TOKEN_KEY);
}

export function logout(): void {
  localStorage.removeItem(TOKEN_KEY);
}

// ─── Core Analysis Operations ────────────────────────────────────────────────

export async function analyzeCode(file: File, carbonRegion: string = 'Global'): Promise<AnalysisResult> {
  const form = new FormData();
  form.append('file', file);
  form.append('carbon_region', carbonRegion);

  const res = await fetch(`${BASE}/analyze`, {
    method: 'POST',
    headers: {
      ...getAuthHeaders(),
    },
    body: form,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(err.detail || `Server error ${res.status}`);
  }
  return res.json();
}

export async function downloadReport(file: File, format: 'pdf' | 'md' = 'pdf'): Promise<void> {
  const form = new FormData();
  form.append('file', file);

  const url = format === 'pdf' ? '/report/pdf' : '/report/markdown';
  const res = await fetch(`${BASE}${url}`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: form,
  });
  if (!res.ok) throw new Error('Report generation failed');

  const blob = await res.blob();
  const blobUrl = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = blobUrl;
  link.download = `greendev_report.${format === 'pdf' ? 'pdf' : 'md'}`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  setTimeout(() => {
    window.URL.revokeObjectURL(blobUrl);
  }, 200);
}

export async function downloadReportById(analysisId: number, format: 'pdf' | 'md' = 'pdf'): Promise<void> {
  const res = await fetch(`${BASE}/report/${analysisId}/download?format=${format}`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });
  if (!res.ok) throw new Error('Report download failed');

  const blob = await res.blob();
  const blobUrl = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = blobUrl;
  link.download = `greendev_report_${analysisId}.${format === 'pdf' ? 'pdf' : 'md'}`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  setTimeout(() => {
    window.URL.revokeObjectURL(blobUrl);
  }, 200);
}

export async function checkHealth(): Promise<{ status: string; timestamp: string }> {
  const res = await fetch(`${BASE}/health`);
  return res.json();
}

// ─── Settings / Profile & Preferences Management ──────────────────────────────

export async function loadSettings(): Promise<UserSettings> {
  const [profile, prefs] = await Promise.all([
    apiFetch('/profile'),
    apiFetch('/preferences'),
  ]);

  return {
    name: profile.name || '',
    email: profile.email || '',
    org: profile.organization || '',
    carbon_region: prefs.carbon_region || 'Global',
    report_format: prefs.report_format || 'PDF',
    notify_analysis: !!prefs.notify_analysis,
    notify_updates: !!prefs.notify_updates,
    notify_marketing: !!prefs.notify_marketing,
    notify_alerts: !!prefs.notify_alerts,
    created_at: profile.created_at,
  };
}

export async function saveSettings(settings: UserSettings): Promise<void> {
  await Promise.all([
    apiFetch('/profile', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: settings.name,
        email: settings.email,
        organization: settings.org,
      }),
    }),
    apiFetch('/preferences', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        carbon_region: settings.carbon_region,
        report_format: settings.report_format,
        notify_analysis: settings.notify_analysis ? 1 : 0,
        notify_updates: settings.notify_updates ? 1 : 0,
        notify_marketing: settings.notify_marketing ? 1 : 0,
        notify_alerts: settings.notify_alerts ? 1 : 0,
      }),
    }),
  ]);
}

// ─── Account Deletion ─────────────────────────────────────────────────────────

export async function deleteAccount(): Promise<void> {
  await apiFetch('/account', { method: 'DELETE' });
  clearAllData();
}

export function clearAllData(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem('greendev-theme');
}

// ─── API Key Management ───────────────────────────────────────────────────────

export async function listApiKeys(): Promise<ApiKeyEntry[]> {
  return apiFetch('/api-keys');
}

export async function generateApiKey(name: string = "Default Key"): Promise<ApiKeyEntry> {
  const res = await apiFetch('/api-keys', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name }),
  });
  return res.key;
}

export async function revokeApiKey(id: number): Promise<void> {
  await apiFetch(`/api-keys/${id}`, { method: 'DELETE' });
}

// ─── Billing / Plans ──────────────────────────────────────────────────────────

export async function getBillingPlan(): Promise<BillingPlanInfo> {
  return apiFetch('/billing/plan');
}

export async function getBillingUsage(): Promise<BillingUsageInfo> {
  return apiFetch('/billing/usage');
}

// ─── Analytics ────────────────────────────────────────────────────────────────

export async function getAnalyticsUsage(): Promise<AnalyticsUsageInfo> {
  return apiFetch('/analytics/usage');
}

export async function getAnalyticsHistory(): Promise<HistoryEntry[]> {
  return apiFetch('/analytics/history');
}

// ─── Carbon Trajectory ────────────────────────────────────────────────────────

export interface TrajectoryData {
  monthly_labels: string[];
  current_emissions: number[];
  optimized_emissions: number[];
  percentage_reduction: number;
  cumulative_savings: number;
}

export async function getAnalysisProjection(analysisId: number): Promise<TrajectoryData> {
  return apiFetch(`/analysis/${analysisId}/projection`);
}

// ─── Help Center Content (CMS) ────────────────────────────────────────────────

export async function getHelpArticles(): Promise<any[]> {
  return apiFetch('/help');
}

export async function getFaqList(): Promise<any[]> {
  return apiFetch('/faq');
}

// ─── Language Benchmarks Notes ────────────────────────────────────────────────

export async function getBenchmarkNotes(): Promise<LanguageBenchmarkNote[]> {
  return apiFetch('/benchmarks/languages');
}

// ─── Sample Scripts ───────────────────────────────────────────────────────────

export async function getSampleScripts(): Promise<SampleScript[]> {
  return apiFetch('/samples');
}
