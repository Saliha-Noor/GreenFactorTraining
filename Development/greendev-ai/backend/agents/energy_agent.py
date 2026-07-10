"""
Agent 2 — Energy Agent
Executes the uploaded Python code and measures energy consumption
using CodeCarbon's EmissionsTracker.
"""

import io
import time
import traceback
import contextlib
from codecarbon import EmissionsTracker


def measure_energy(code_string: str) -> dict:
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    exec_error     = None
    start_time     = time.perf_counter()
    tracker        = None
    emissions_data = None

    try:
        tracker = EmissionsTracker(
            measure_power_secs=1,
            log_level="error",
            save_to_file=False,
            allow_multiple_runs=True,
        )
        tracker.start()
    except Exception as e:
        stderr_capture.write(f"CodeCarbon initialization fallback: {e}\n")
        tracker = None

    try:
        with contextlib.redirect_stdout(stdout_capture), \
             contextlib.redirect_stderr(stderr_capture):
            exec(compile(code_string, "<user_code>", "exec"), {})
    except Exception:
        exec_error = traceback.format_exc()
    finally:
        if tracker is not None:
            try:
                emissions_data = tracker.stop()
            except Exception:
                pass

    elapsed = time.perf_counter() - start_time

    # Calculate metrics
    energy_kwh = 0.0
    co2_grams  = 0.0
    mode       = "CodeCarbon"

    if tracker is not None and getattr(tracker, "_total_energy", None) is not None:
        energy_kwh = float(tracker._total_energy.kWh) if tracker._total_energy.kWh else 0.0
        co2_grams  = float(emissions_data) * 1000 if emissions_data else 0.0
        if "falling back" in (stderr_capture.getvalue() or "").lower():
            mode = "TDP-estimation (no RAPL)"
    else:
        # Fallback heuristic calculation if CodeCarbon failed (e.g., inside VMs or without hardware access)
        # Pakistan average grid carbon intensity (gCO2eq/kWh) = 357.0
        # Assume a standard laptop CPU consumes ~15W of power = 0.015 kW
        # energy_kwh = kW * hours = 0.015 * (elapsed / 3600)
        energy_kwh = 0.015 * (elapsed / 3600)
        co2_grams  = energy_kwh * 357.0
        mode       = "TDP-estimation (Fallback)"

    # Ensure a sensible minimum floor for micro-benchmarks so UI metrics are readable
    if energy_kwh < 0.00001:
        energy_kwh = max(0.00001, elapsed * 0.0005)
        co2_grams  = energy_kwh * 357.0

    return {
        "energy_kwh":      round(energy_kwh, 10),
        "co2_grams":       round(co2_grams, 8),
        "execution_time":  round(elapsed, 4),
        "stdout":          stdout_capture.getvalue(),
        "stderr":          stderr_capture.getvalue(),
        "exec_error":      exec_error,
        "mode":            mode,
    }
