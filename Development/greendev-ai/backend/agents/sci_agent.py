"""
Agent 4 — SCI Agent
Calculates the Software Carbon Intensity (SCI) score using both
the estimated (CodeCarbon) and real (RAPL dataset) energy values.

Formula:
    SCI = (E × I + M) / R

Where:
    E = Energy consumed (kWh)
    I = Carbon intensity of the grid (gCO2eq/kWh)
    M = Embodied carbon of hardware (gCO2eq)
    R = Functional unit (1 run)
"""

# Pakistan average grid carbon intensity (gCO2eq/kWh) — IEA estimate
DEFAULT_CARBON_INTENSITY = 357.0  # gCO2eq/kWh

# Embodied carbon per hour of device use (HP EliteBook i5, ~2012 vintage)
# Lifecycle: ~400 kg CO2, 4-year life, 8h/day → 400000g / (4*365*8) ≈ 34g/hour
HARDWARE_CARBON_PER_HOUR = 34.0   # gCO2eq/hour

# Functional unit: 1 execution run
FUNCTIONAL_UNIT = 1


def _joules_to_kwh(joules: float) -> float:
    return joules / 3_600_000


def calculate_sci(
    energy_kwh: float,
    execution_time_seconds: float,
    carbon_intensity: float = DEFAULT_CARBON_INTENSITY,
    hardware_carbon_per_hour: float = HARDWARE_CARBON_PER_HOUR,
    functional_unit: int = FUNCTIONAL_UNIT,
) -> float:
    hours    = execution_time_seconds / 3600
    hardware = hardware_carbon_per_hour * hours
    sci      = (energy_kwh * carbon_intensity + hardware) / functional_unit
    return round(sci, 8)


def get_sci_scores(energy_data: dict, benchmark_data: dict,
                    carbon_intensity: float = None) -> dict:
    ci = carbon_intensity if carbon_intensity is not None else DEFAULT_CARBON_INTENSITY

    # Estimated SCI (from CodeCarbon)
    estimated_sci = calculate_sci(
        energy_kwh             = energy_data["energy_kwh"],
        execution_time_seconds = energy_data["execution_time"],
        carbon_intensity       = ci,
    )

    # Real SCI (from RAPL dataset — Python row)
    python_bench  = benchmark_data.get("python", {})
    rapl_joules   = python_bench.get("energy_joules", 0)
    rapl_time     = python_bench.get("time_seconds", energy_data["execution_time"])
    rapl_kwh      = _joules_to_kwh(rapl_joules)

    real_sci = calculate_sci(
        energy_kwh             = rapl_kwh,
        execution_time_seconds = rapl_time,
        carbon_intensity       = ci,
    )

    # Deviation percentage
    deviation_pct = 0.0
    if real_sci > 0:
        deviation_pct = round(abs(estimated_sci - real_sci) / real_sci * 100, 2)

    return {
        "estimated_sci":     estimated_sci,
        "real_sci":          real_sci,
        "deviation_pct":     deviation_pct,
        "anomaly_detected":  deviation_pct > 50,
        "carbon_intensity":  ci,
        "functional_unit":   FUNCTIONAL_UNIT,
    }
