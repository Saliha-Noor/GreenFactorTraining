import sqlite3
import os
import hashlib
import hmac
import base64
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "greendev.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON;")
    yield conn

def init_db():
    # If the database does not exist or tables are missing, create them.
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        name TEXT,
        organization TEXT,
        password_hash TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Preferences table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_preferences (
        user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
        carbon_region TEXT DEFAULT 'Global',
        report_format TEXT DEFAULT 'PDF',
        notify_analysis INTEGER DEFAULT 1,
        notify_weekly INTEGER DEFAULT 0,
        notify_security INTEGER DEFAULT 1,
        notify_updates INTEGER DEFAULT 1,
        notify_marketing INTEGER DEFAULT 0,
        notify_alerts INTEGER DEFAULT 1
    );
    """)

    # 3. API keys table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS api_keys (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
        key_string TEXT UNIQUE NOT NULL,
        name TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        last_used_at TEXT,
        usage_count INTEGER DEFAULT 0,
        is_active INTEGER DEFAULT 1
    );
    """)

    # 4. Subscriptions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subscriptions (
        user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
        plan_type TEXT DEFAULT 'Local Plan',
        limits INTEGER DEFAULT -1,
        quota INTEGER DEFAULT -1,
        expiration TEXT,
        status TEXT DEFAULT 'Active'
    );
    """)

    # 5. Analytics table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analytics (
        user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
        total_requests INTEGER DEFAULT 0,
        daily_requests INTEGER DEFAULT 0,
        monthly_requests INTEGER DEFAULT 0,
        last_request_timestamp TEXT,
        total_analyses INTEGER DEFAULT 0,
        successful_analyses INTEGER DEFAULT 0,
        failed_analyses INTEGER DEFAULT 0,
        total_processing_time REAL DEFAULT 0.0
    );
    """)

    # 6. History table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
        filename TEXT NOT NULL,
        score REAL NOT NULL,
        co2_grams REAL NOT NULL,
        savings_kg REAL NOT NULL,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        result_json TEXT
    );
    """)

    # 7. Help Articles table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS help_articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_index INTEGER NOT NULL,
        category_name TEXT NOT NULL,
        heading TEXT NOT NULL,
        body TEXT NOT NULL,
        display_order INTEGER DEFAULT 0
    );
    """)

    # 8. FAQs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS faqs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_index INTEGER NOT NULL,
        question TEXT NOT NULL,
        answer TEXT NOT NULL,
        display_order INTEGER DEFAULT 0
    );
    """)

    # 9. Video Tutorials table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS video_tutorials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_index INTEGER NOT NULL,
        title TEXT NOT NULL,
        duration TEXT NOT NULL,
        url TEXT DEFAULT '',
        thumbnail TEXT DEFAULT '',
        display_order INTEGER DEFAULT 0
    );
    """)

    # 10. Benchmark Notes table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS benchmark_notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        language TEXT UNIQUE NOT NULL,
        factor REAL NOT NULL,
        energy_notes TEXT NOT NULL,
        runtime_notes TEXT NOT NULL,
        rapl_notes TEXT NOT NULL,
        display_order INTEGER DEFAULT 0
    );
    """)

    # 11. Sample Scripts table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sample_scripts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT UNIQUE NOT NULL,
        score REAL NOT NULL,
        verdict TEXT NOT NULL,
        color TEXT NOT NULL,
        source_code TEXT NOT NULL,
        display_order INTEGER DEFAULT 0
    );
    """)

    conn.commit()

    # Seed static content tables if empty
    seed_static_content(conn)
    conn.close()

def seed_static_content(conn):
    cursor = conn.cursor()

    # Check if help articles are empty
    cursor.execute("SELECT COUNT(*) FROM help_articles")
    if cursor.fetchone()[0] == 0:
        help_data = [
            # 0: Green Score
            (0, "Green Score", "How the score is calculated", "Four sub-scores contribute equally: Performance (runtime efficiency), Energy (kWh per execution), Carbon (CO₂ equivalent), and Maintainability (cyclomatic complexity). Each is normalised to 0–10 and averaged into the final score.", 0),
            (0, "Green Score", "SCI — Software Carbon Intensity", "SCI is an ISO 21031 standard metric expressed as kgCO₂eq per 1 000 functional runs. GreenDevAI computes an estimated SCI (from static analysis) and a real SCI (from live RAPL). The deviation between them indicates measurement confidence.", 1),
            (0, "Green Score", "Verdict labels", "Efficient (≥7.5): your code is already in the top efficiency tier. Moderate (5–7.4): meaningful improvements are possible. Needs Work (<5): significant energy waste detected — prioritise the hotspot fixes immediately.", 2),
            
            # 1: Energy Metrics
            (1, "Energy Metrics", "What RAPL measures", "RAPL reads CPU package power, core power, and DRAM power simultaneously. GreenDevAI runs 1 000 warm iterations to eliminate cold-start noise, then averages the per-run energy cost to a stable figure.", 0),
            (1, "Energy Metrics", "Reading the kWh number", "1.247 kWh per 1 000 runs means this function, called 1 000 times, consumes 1.247 kilowatt-hours — equivalent to a 60 W bulb running for ~21 hours. Optimised code typically reduces this by 40–60%.", 1),
            (1, "Energy Metrics", "Hotspot identification", "The hotspot is the function responsible for the highest share of total energy. GreenDevAI cross-validates static AST loop-depth analysis with the live RAPL profile to confirm the finding with ≥90% confidence.", 2),

            # 2: RAPL Benchmark
            (2, "RAPL Benchmark", "Benchmark methodology", "GreenDevAI compiles reference implementations of the detected algorithmic pattern (matrix ops, sorting, graph traversal) in C, C++ (−O2), and Java (JVM warm). The 'Energy factor' shows how many times more energy Python uses relative to C.", 0),
            (2, "RAPL Benchmark", "Interpreting the energy factor", "A factor of 100× means Python uses 100× more energy than C for equivalent work. This is typical for tight numerical loops without NumPy. With vectorisation, the factor often drops to 5–15×.", 1),
            (2, "RAPL Benchmark", "Java vs Python", "Java's JIT compiler closes much of the gap with C after warm-up. Python without NumPy often exceeds Java by 5–20×. NumPy code can match Java for array-heavy workloads.", 2),

            # 3: Carbon Projection
            (3, "Carbon Projection", "Carbon intensity by region", "Carbon intensity (gCO₂eq/kWh) varies by electricity grid: EU average ≈ 280, UK ≈ 210, US average ≈ 390, global ≈ 460. Update your region in Profile → Preferences to get an accurate local projection.", 0),
            (3, "Carbon Projection", "Reading the chart", "The orange line shows your current CO₂ trajectory over 12 months. The green line shows the projected trajectory after applying the top recommended optimisation. The gap between them is your potential annual saving.", 1),
            (3, "Carbon Projection", "Real-world equivalents", "19.6 kg CO₂ is equivalent to driving ~120 km in an average petrol car, or manufacturing ~1.5 kg of beef. These analogues help communicate impact to non-technical stakeholders.", 2),

            # 4: Planner Agent
            (4, "Planner Agent", "Task decomposition", "The Planner parses the dependency graph of the seven analysis agents. Agents with no shared data inputs (Energy and Benchmark) are spawned in parallel, cutting total wall-clock time by ~46% versus sequential execution.", 0),
            (4, "Planner Agent", "Anomaly detection", "After Energy and SCI results arrive, the Planner checks whether real SCI deviates from estimated SCI by more than ±15%. A deviation above that threshold triggers a re-run of the Energy agent with extended sampling.", 1),
            (4, "Planner Agent", "Confidence scoring", "Confidence combines: agreement between static AST analysis and RAPL profiling on hotspot location, SCI deviation within the normal band, and benchmark variance below 5%. 94% means all three checks passed.", 2),

            # 5: Export Report
            (5, "Export Report", "PDF report", "A formatted, print-ready document with embedded charts, an executive summary, detailed findings per agent, ISO 21031 citations, and a methodology appendix. Typically 8–12 pages for a medium-complexity file.", 0),
            (5, "Export Report", "Markdown report", "A structured .md file suitable for GitHub PRs, Notion, Confluence, or CI pipeline artefacts. Includes all tables and a text-based chart representation. Ideal for automated green-software gates in CI/CD.", 1),
            (5, "Export Report", "Privacy & compliance", "GreenDevAI runs entirely in your browser. Reports are generated client-side and downloaded directly — no file content or results are ever transmitted to our servers. Reports include an analysis ID for traceability.", 2)
        ]
        cursor.executemany(
            "INSERT INTO help_articles (category_index, category_name, heading, body, display_order) VALUES (?, ?, ?, ?, ?)",
            help_data
        )

    # Check if FAQs are empty
    cursor.execute("SELECT COUNT(*) FROM faqs")
    if cursor.fetchone()[0] == 0:
        faq_data = [
            (0, "Why is my score lower than expected?", "Nested loops, redundant I/O calls, and non-vectorised array operations are the most common score reducers. Open the Energy tab to see the exact hotspot lines.", 0),
            (0, "How do I reach 8+?", "Apply the top hotspot fix — usually an np.einsum or vectorisation rewrite — then re-run. Most codebases see a 1.5–2 point jump from a single fix.", 1),
            (0, "Is the score comparable across projects?", "Yes. All scores are normalised against a reference baseline so a 7.2 on a 50-line script equals a 7.2 on a 2 000-line module.", 2),
            
            (1, "Why 1 000 iterations?", "Averaging across many iterations eliminates OS scheduling noise, CPU frequency scaling events, and cache cold-start effects — giving a reproducible, stable energy reading.", 0),
            (1, "What if RAPL isn't available?", "GreenDevAI falls back to a power-model estimation using CPU frequency and instruction counts. Accuracy drops from ±2% to ±8% but remains sufficient for ranking hotspots.", 1),
            (1, "What does 'warm cache' mean?", "The first few iterations are discarded because the L1/L2 cache is cold and branch predictors haven't learned the code's patterns. Warmup ensures we measure steady-state cost.", 2),

            (2, "Why compare to C specifically?", "C is the de facto baseline in energy-efficiency research (Green Software Foundation, ACM studies) because it has minimal runtime overhead and provides a theoretical lower bound.", 0),
            (2, "Can I beat the Python average?", "Yes — code using NumPy, Cython, or Numba routinely achieves 5–20× the energy cost of C rather than 40–100×. Vectorisation is the single biggest lever.", 1),
            (2, "Does this account for developer time?", "No — GreenDevAI measures runtime energy only. Refactoring costs are outside scope, but the Carbon tab helps you quantify the long-term environmental payoff.", 2),

            (3, "How accurate is the projection?", "±15% under the ISO 21031 methodology. The main source of uncertainty is variation in your grid's carbon intensity over time. Updating your region in Preferences improves accuracy.", 0),
            (3, "What is kgCO₂eq?", "Kilograms of CO₂ equivalent — a unit that combines CO₂, methane, and nitrous oxide from electricity generation, weighted by their global-warming potential.", 1),
            (3, "Can I export the chart data?", "Yes — the Export tab includes the 12-month projection table as a CSV-formatted block inside both the PDF and Markdown reports.", 2),

            (4, "What triggers a re-run?", "SCI deviation >±15%, benchmark variance >5%, or an unexpected runtime exception in any agent. All re-run decisions are logged in the Reasoning block.", 0),
            (4, "Can I configure the Planner?", "Not via the UI, but the API exposes planner_config parameters for anomaly thresholds, max re-runs, and parallelism limits for enterprise users.", 1),
            (4, "How much time does the Planner add?", "The Planner itself takes ~900 ms. The parallel execution it enables saves 2–4 s on a typical file, so it is net-positive in all cases.", 2),

            (5, "Can I customise the report template?", "Pro plan users can add a custom logo. Enterprise plan allows full template customisation via a Handlebars template API.", 0),
            (5, "What citations are included?", "ISO 21031:2022 (SCI), Pereira et al. 2017 (energy language benchmarks), Green Software Foundation methodology, and IPCC AR6 carbon intensity figures.", 1),
            (5, "Can I re-run the analysis later?", "Yes — upload the same file again. GreenDevAI detects if the file hash matches a recent run and offers to load cached results instead of re-running all agents.", 2)
        ]
        cursor.executemany(
            "INSERT INTO faqs (category_index, question, answer, display_order) VALUES (?, ?, ?, ?)",
            faq_data
        )

    # Check if videos are empty
    cursor.execute("SELECT COUNT(*) FROM video_tutorials")
    if cursor.fetchone()[0] == 0:
        video_data = [
            (0, "Understanding Your Green Score", "4:32", "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "https://img.youtube.com/vi/dQw4w9WgXcQ/0.jpg", 0),
            (0, "Sub-score Deep Dive", "6:15", "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "https://img.youtube.com/vi/dQw4w9WgXcQ/0.jpg", 1),
            (1, "How RAPL Energy Profiling Works", "5:48", "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "https://img.youtube.com/vi/dQw4w9WgXcQ/0.jpg", 0),
            (1, "Interpreting Energy Metrics", "3:20", "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "https://img.youtube.com/vi/dQw4w9WgXcQ/0.jpg", 1),
            (2, "Cross-Language Energy Benchmarking", "7:02", "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "https://img.youtube.com/vi/dQw4w9WgXcQ/0.jpg", 0),
            (2, "Closing the Gap with NumPy", "4:55", "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "https://img.youtube.com/vi/dQw4w9WgXcQ/0.jpg", 1),
            (3, "Carbon Projection Methodology", "5:10", "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "https://img.youtube.com/vi/dQw4w9WgXcQ/0.jpg", 0),
            (3, "Communicating Carbon Impact", "3:44", "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "https://img.youtube.com/vi/dQw4w9WgXcQ/0.jpg", 1),
            (4, "Inside the Planner Agent", "6:30", "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "https://img.youtube.com/vi/dQw4w9WgXcQ/0.jpg", 0),
            (4, "Multi-Agent Pipeline Overview", "8:15", "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "https://img.youtube.com/vi/dQw4w9WgXcQ/0.jpg", 1),
            (5, "Exporting and Sharing Reports", "3:05", "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "https://img.youtube.com/vi/dQw4w9WgXcQ/0.jpg", 0),
            (5, "Using Reports in CI/CD Pipelines", "5:22", "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "https://img.youtube.com/vi/dQw4w9WgXcQ/0.jpg", 1)
        ]
        cursor.executemany(
            "INSERT INTO video_tutorials (category_index, title, duration, url, thumbnail, display_order) VALUES (?, ?, ?, ?, ?, ?)",
            video_data
        )

    # Check if benchmark notes are empty
    cursor.execute("SELECT COUNT(*) FROM benchmark_notes")
    if cursor.fetchone()[0] == 0:
        bench_data = [
            ("Python", 100.0, "Interpreter + GIL overhead", "Steady single-thread runtime", "CodeCarbon estimated baseline", 0),
            ("C", 1.0, "Bare metal · no runtime", "No garbage collection overhead", "Direct hardware instructions", 1),
            ("C++", 1.1, "Templates amortised at -O2", "Compiler-optimized template code", "Direct hardware instructions", 2),
            ("Java", 8.2, "JVM JIT · warm-up cost", "Just-In-Time compiled bytecode", "DRAM and CPU package profiling", 3)
        ]
        cursor.executemany(
            "INSERT INTO benchmark_notes (language, factor, energy_notes, runtime_notes, rapl_notes, display_order) VALUES (?, ?, ?, ?, ?, ?)",
            bench_data
        )

    # Check if sample scripts are empty
    cursor.execute("SELECT COUNT(*) FROM sample_scripts")
    if cursor.fetchone()[0] == 0:
        sample_data = [
            ("matrix_solver.py", 7.8, "Efficient", "#22c55e", """import numpy as np

def compute_similarity(embeddings: list) -> np.ndarray:
    n = len(embeddings)
    result = np.zeros((n, n))
    for i in range(n):                 # 42% of runtime
        for j in range(n):
            result[i][j] = np.dot(embeddings[i], embeddings[j])
    return result
""", 0),
            ("image_pipeline.py", 5.4, "Moderate", "#f59e0b", """import os
from PIL import Image

def process_images(directory):
    # Unoptimized I/O and resizing loops
    files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.jpg')]
    images = []
    for file in files:
        img = Image.open(file)
        # Resizing without draft downscale speeds
        img = img.resize((1024, 1024))
        images.append(img)
    return images
""", 1),
            ("data_loader.py", 9.1, "Excellent", "#3b82f6", """# Clean generator data loading
def load_data_generator(filepath):
    with open(filepath, 'r') as f:
        for line in f:
            yield line.strip().split(',')
""", 2)
        ]
        cursor.executemany(
            "INSERT INTO sample_scripts (filename, score, verdict, color, source_code, display_order) VALUES (?, ?, ?, ?, ?, ?)",
            sample_data
        )

    conn.commit()

# Call init_db on import to make sure database is ready
init_db()
