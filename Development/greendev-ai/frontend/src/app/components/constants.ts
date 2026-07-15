export const AGENTS = [
  { id: "parse",  label: "Code Analysis",    sub: "ast.parse · McCabe complexity",  start: 0,    end: 1100 },
  { id: "plan",   label: "Planner",          sub: "task graph · dependency resolve", start: 1200, end: 2100 },
  { id: "energy", label: "Energy",           sub: "perf_event · RAPL counters",     start: 2200, end: 3900 },
  { id: "bench",  label: "Benchmark",        sub: "C · C++ · Java · baseline diff", start: 2200, end: 4300 },
  { id: "sci",    label: "SCI",              sub: "ISO 21031 · carbon intensity",   start: 4400, end: 5200 },
  { id: "rec",    label: "Recommendation",   sub: "np.einsum · cache · generator",  start: 5300, end: 6000 },
  { id: "report", label: "Report Generator", sub: "PDF · Markdown · JSON",          start: 6100, end: 6700 },
] as const;

export type AgentId = typeof AGENTS[number]["id"];

export const LOG_LINES = [
  { t: 100,  id: "parse",  msg: "Opened code file for AST parsing..." },
  { t: 400,  id: "parse",  msg: "Analysing functions, loops, and recursions..." },
  { t: 800,  id: "parse",  msg: "AST parsing complete. Calculating cyclomatic complexity..." },
  { t: 1200, id: "plan",   msg: "Planner resolving multi-agent task execution plan..." },
  { t: 1600, id: "plan",   msg: "Decided execution graph: parallelizing energy and benchmarks" },
  { t: 2200, id: "energy", msg: "Initializing CodeCarbon tracker..." },
  { t: 2200, id: "bench",  msg: "Querying RAPL baselines from energy-languages dataset..." },
  { t: 2800, id: "energy", msg: "Executing code iterations to measure steady-state power draw..." },
  { t: 3200, id: "bench",  msg: "Comparing Python CPU & memory footprint with native counterparts..." },
  { t: 3600, id: "energy", msg: "Live energy profiling complete. Storing emissions metrics..." },
  { t: 4400, id: "sci",    msg: "Calculating Software Carbon Intensity (SCI) score..." },
  { t: 4900, id: "sci",    msg: "SCI model complete. Running variance assessment..." },
  { t: 5300, id: "rec",    msg: "Recommendation agent analyzing AST for energy-saving patterns..." },
  { t: 5700, id: "rec",    msg: "Gemini generating code refactor plans & line-level hotfixes..." },
  { t: 6100, id: "report", msg: "Orchestrating PDF & Markdown report compilation..." },
  { t: 6500, id: "report", msg: "Analysis cycle finished successfully. Finalizing scores." },
];

export const PIPELINE_STEPS = [
  { num: "01", name: "Code Analysis",    detail: "AST parse · McCabe complexity",   color: "#60a5fa" },
  { num: "02", name: "Energy",           detail: "RAPL measurement · watt·hour",     color: "#22c55e" },
  { num: "03", name: "Benchmark",        detail: "vs C, C++, Java runtimes",         color: "#a78bfa" },
  { num: "04", name: "SCI Score",        detail: "software carbon intensity index",  color: "#f59e0b" },
  { num: "05", name: "Recommendations",  detail: "vectorization & refactor hints",   color: "#22c55e" },
];

export const DUMMY_SCRIPTS: Record<string, string> = {
  "matrix_solver.py": `import numpy as np

def compute_similarity(embeddings: list) -> np.ndarray:
    n = len(embeddings)
    result = np.zeros((n, n))
    for i in range(n):                 # 42% of runtime
        for j in range(n):
            result[i][j] = np.dot(embeddings[i], embeddings[j])
    return result
`,
  "image_pipeline.py": `import os
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
`,
  "data_loader.py": `# Clean generator data loading
def load_data_generator(filepath):
    with open(filepath, 'r') as f:
        for line in f:
            yield line.strip().split(',')
`
};
