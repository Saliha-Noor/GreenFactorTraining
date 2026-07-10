"""
Planner Agent — Orchestrator
Dynamically decides which agents to run and in what order,
based on code metrics. Performs reflection on SCI results
and can attach anomaly notes to downstream agents.
"""

import json
import re
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def _parse_json(text: str) -> dict:
    text = re.sub(r"```json|```", "", text).strip()
    return json.loads(text)


def build_execution_plan(code_stats: dict) -> dict:
    """
    Phase 1 — Before running agents.
    Decide which agents to run and in what order.
    """
    try:
        model  = genai.GenerativeModel("gemini-1.5-flash")
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
        return _parse_json(response.text)
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
        return _parse_json(response.text)
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

