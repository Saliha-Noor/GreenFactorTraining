"""
Planner Agent — Orchestrator
Dynamically decides which agents to run and in what order,
based on code metrics. Performs reflection on SCI results
and can attach anomaly notes to downstream agents.
"""

import json
import re
import os
from google import genai
try:
    from dotenv import load_dotenv
except Exception:
    def load_dotenv():
        return None

load_dotenv()
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
except Exception:
    # If configuration fails at import time, defer to runtime (fallbacks exist)
    pass


def _extract_response_text(resp) -> str:
    # Try common response shapes from different genai SDK versions
    if resp is None:
        return ""

    # Direct text attribute
    if isinstance(resp, str):
        return resp

    for attr in ("text", "content", "output", "response"):
        val = getattr(resp, attr, None)
        if isinstance(val, str) and val.strip():
            return val

    # Some SDKs return sequences like .candidates, .outputs, .result
    for seq_attr in ("candidates", "outputs", "result", "responses", "choices"):
        seq = getattr(resp, seq_attr, None)
        if seq:
            try:
                first = seq[0]
                if isinstance(first, dict):
                    for key in ("content", "text"):
                        if key in first and isinstance(first[key], str):
                            return first[key]
                else:
                    cont = getattr(first, "content", None) or getattr(first, "text", None)
                    if isinstance(cont, str):
                        return cont
            except Exception:
                pass

    # Fallback: string conversion
    try:
        return str(resp)
    except Exception:
        return ""


def _parse_json(text: str) -> dict:
    if not isinstance(text, str):
        text = str(text or "")

    # Strip Markdown fences
    text = re.sub(r"```json|```", "", text).strip()

    # Attempt to extract the first JSON object in the text
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = text[start:end + 1]
    else:
        candidate = text

    return json.loads(candidate)


def build_execution_plan(code_stats: dict) -> dict:
    """
    Phase 1 — Before running agents.
    Decide which agents to run and in what order.
    """
    try:
        model  = genai.GenerativeModel("gemini-2.5-flash")
        prompt = f"""
You are an orchestration planner for GreenDev AI, a multi-agent green-coding analysis system.

Available agents (tools):
- energy_agent      : measures actual energy + CO2 (CodeCarbon). Run ALWAYS.
- benchmark_agent   : fetches real RAPL reference from dataset. Run if task type is known and not trivial.
- sci_agent         : calculates SCI metric. Run only if both energy_agent and benchmark_agent ran.
- recommendation_agent : generates Green Score + Carbon Projection via Gemini. Run ALWAYS last.

Code analysis result:
{json.dumps(code_stats, indent=2)}

Decide:
1. Which agents to include in the plan.
2. Whether energy_agent and benchmark_agent can be treated as parallel (they are independent).
3. Any reasoning for skipping an agent.

Return ONLY valid JSON (no markdown, no preamble):
{{
  "plan": ["energy_agent", "benchmark_agent", "sci_agent", "recommendation_agent"],
  "parallel_phase": ["energy_agent", "benchmark_agent"],
  "skip_reason": {{
    "benchmark_agent": null
  }},
  "reasoning": "short string"
}}
"""
        response = model.generate_content(prompt)
        raw = _extract_response_text(response)
        return _parse_json(raw)
    except Exception as e:
        # Fallback: always run full pipeline
        return {
            "plan": ["energy_agent", "benchmark_agent", "sci_agent", "recommendation_agent"],
            "parallel_phase": ["energy_agent", "benchmark_agent"],
            "skip_reason": {},
            "reasoning": f"Orchestrated parallel execution graph: running energy and benchmark agents concurrently. (Fallback: Gemini inactive)",
        }


def reflect_on_results(code_stats: dict, energy_data: dict,
                        benchmark_data: dict, sci_scores: dict) -> dict:
    """
    Phase 2 — After SCI Agent runs.
    Check for anomalies; decide if re-run is needed or attach reflection notes.
    """
    try:
        model  = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"""
You are the reflection module of GreenDev AI's orchestration system.

The pipeline has completed data collection. Review these results and detect anomalies.

Code stats:      {json.dumps(code_stats)}
Energy data:     {json.dumps(energy_data)}
Benchmark data:  {json.dumps(benchmark_data)}
SCI scores:      {json.dumps(sci_scores)}

Anomaly indicators:
- If estimated_sci and real_sci differ by more than 50%, flag it.
- If energy_kwh is zero or suspiciously low for the code's complexity, flag it.
- If execution_time is < 0.001 seconds for complex code, flag it.

Return ONLY valid JSON (no markdown, no preamble):
{{
  "anomaly_detected": true or false,
  "anomaly_reason": "string or null",
  "rerun_needed": false,
  "reflection_note": "string — this will be passed to the Recommendation Agent as extra context",
  "confidence": "high | medium | low"
}}
"""
        response = model.generate_content(prompt)
        raw = _extract_response_text(response)
        return _parse_json(raw)
    except Exception:
        deviation = sci_scores.get("deviation_pct", 0.0)
        anomaly = deviation > 15.0 or energy_data.get("energy_kwh", 0.0) == 0.0 or energy_data.get("execution_time", 0.0) < 0.001
        
        reason = None
        if anomaly:
            if deviation > 15.0:
                reason = f"SCI deviation is {deviation:.1f}%, exceeding the ±15% hardware benchmark variance limit."
            elif energy_data.get("energy_kwh", 0.0) == 0.0:
                reason = "Energy measurement returned 0.0 kWh (unprivileged execution or virtualized CPU environments)."
            else:
                reason = "Execution completed too quickly to establish a stable energy measurement baseline."
        
        return {
            "anomaly_detected":  anomaly,
            "anomaly_reason":    reason,
            "rerun_needed":      False,
            "reflection_note":   f"Telemetry flagged: {reason}" if reason else "All agent metrics are aligned. Deviation is within normal grid variance bands.",
            "confidence":        "high" if not anomaly else "medium",
        }

