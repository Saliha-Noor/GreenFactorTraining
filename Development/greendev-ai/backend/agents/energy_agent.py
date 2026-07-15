"""
Agent 2 — Energy Agent
Executes the uploaded Python code and measures energy consumption
using CodeCarbon's EmissionsTracker.
"""

import io
import time
import traceback
import contextlib
import sys
import os
import subprocess
import tempfile
from codecarbon import EmissionsTracker

try:
    import resource
except ImportError:
    resource = None


def limit_resources():
    if resource is not None:
        # Limit CPU time to 30 seconds
        resource.setrlimit(resource.RLIMIT_CPU, (30, 30))
        # Limit address space to 512 MB
        resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024, 512 * 1024 * 1024))
        # Limit number of processes
        resource.setrlimit(resource.RLIMIT_NPROC, (10, 10))


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
    except Exception as e:
        stderr_capture.write(f"CodeCarbon initialization fallback: {e}\n")
        tracker = None

    # Write code to temp file
    temp_dir = tempfile.mkdtemp(prefix="greendev_sandbox_")
    temp_file_path = os.path.join(temp_dir, "user_code.py")
    
    preexec = limit_resources if (os.name != 'nt' and resource is not None) else None

    # Start CodeCarbon tracking around the subprocess run
    if tracker is not None:
        try:
            tracker.start()
        except Exception as e:
            stderr_capture.write(f"CodeCarbon start failed: {e}\n")
            tracker = None

    try:
        with open(temp_file_path, "w", encoding="utf-8") as f:
            f.write(code_string)

        res = subprocess.run(
            [sys.executable, temp_file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30.0,
            cwd=temp_dir,
            preexec_fn=preexec
        )
        stdout_capture.write(res.stdout or "")
        stderr_capture.write(res.stderr or "")
        if res.returncode != 0:
            exec_error = f"Process exited with return code {res.returncode}"
    except subprocess.TimeoutExpired as te:
        exec_error = "TimeoutExpired: Code execution exceeded the 30-second limit."
        stdout_capture.write(te.stdout.decode("utf-8") if isinstance(te.stdout, bytes) else (te.stdout or ""))
        stderr_capture.write(te.stderr.decode("utf-8") if isinstance(te.stderr, bytes) else (te.stderr or ""))
    except Exception as e:
        exec_error = f"Subprocess execution failed: {e}\n{traceback.format_exc()}"
    finally:
        if tracker is not None:
            try:
                emissions_data = tracker.stop()
            except Exception:
                pass

        # Cleanup temp file and dir
        try:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)
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
