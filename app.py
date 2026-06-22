import streamlit as st
import os
import json
from dotenv import load_dotenv

load_dotenv()

# ═══════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════
st.set_page_config(
    page_title="Study Agent",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ═══════════════════════════════════════════════
# STYLES
# ═══════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Hide Streamlit defaults */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* App shell */
.app-shell {
    display: flex;
    height: 100vh;
    overflow: hidden;
    background: #F8F9FC;
}

/* Sidebar nav */
.sidebar-nav {
    width: 240px;
    min-width: 240px;
    background: #1C2340;
    height: 100vh;
    display: flex;
    flex-direction: column;
    padding: 0;
    position: fixed;
    left: 0;
    top: 0;
    z-index: 100;
}

.sidebar-brand {
    padding: 28px 24px 20px;
    border-bottom: 1px solid rgba(255,255,255,0.08);
}

.sidebar-brand h1 {
    color: #FFFFFF;
    font-size: 20px;
    font-weight: 700;
    margin: 0;
    letter-spacing: -0.3px;
}

.sidebar-brand p {
    color: rgba(255,255,255,0.45);
    font-size: 12px;
    margin: 4px 0 0;
}

.nav-section-label {
    padding: 20px 24px 8px;
    color: rgba(255,255,255,0.3);
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 1.2px;
    text-transform: uppercase;
}

.nav-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 11px 24px;
    color: rgba(255,255,255,0.55);
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    border-left: 3px solid transparent;
    transition: all 0.15s;
    text-decoration: none;
}

.nav-item:hover {
    background: rgba(255,255,255,0.06);
    color: #FFFFFF;
}

.nav-item.active {
    background: rgba(99,179,237,0.12);
    color: #63B3ED;
    border-left-color: #63B3ED;
}

.nav-item .nav-icon {
    font-size: 16px;
    width: 20px;
    text-align: center;
}

.nav-badge {
    margin-left: auto;
    background: #2D3748;
    color: rgba(255,255,255,0.4);
    font-size: 10px;
    padding: 2px 7px;
    border-radius: 10px;
}

.nav-badge.done {
    background: rgba(72,187,120,0.2);
    color: #48BB78;
}

/* Main content area */
.main-content {
    margin-left: 240px;
    flex: 1;
    height: 100vh;
    overflow-y: auto;
    padding: 40px 48px;
}

/* Page header */
.page-header {
    margin-bottom: 32px;
}

.page-header h2 {
    font-size: 26px;
    font-weight: 700;
    color: #1A202C;
    margin: 0 0 6px;
    letter-spacing: -0.5px;
}

.page-header p {
    color: #718096;
    font-size: 15px;
    margin: 0;
}

/* Cards */
.card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 20px;
}

.card-title {
    font-size: 15px;
    font-weight: 600;
    color: #2D3748;
    margin: 0 0 16px;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Status pills */
.pill {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 500;
}

.pill-done { background: #C6F6D5; color: #22543D; }
.pill-pending { background: #EDF2F7; color: #4A5568; }
.pill-running { background: #BEE3F8; color: #2A4365; }

/* Action buttons */
.stButton > button {
    border-radius: 8px !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    border: none !important;
    transition: all 0.15s !important;
}

/* Primary button */
.stButton > button[kind="primary"] {
    background: #4F6BED !important;
    color: white !important;
    padding: 10px 20px !important;
}

.stButton > button[kind="primary"]:hover {
    background: #3D56D6 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(79,107,237,0.3) !important;
}

/* Secondary button */
.stButton > button[kind="secondary"] {
    background: #EDF2F7 !important;
    color: #2D3748 !important;
}

/* Checkboxes */
.stCheckbox label { font-size: 14px !important; color: #4A5568 !important; }

/* Select boxes */
.stSelectbox > div > div {
    border-radius: 8px !important;
    border-color: #E2E8F0 !important;
    font-size: 14px !important;
}

/* Info / success / error boxes */
.stAlert {
    border-radius: 8px !important;
    font-size: 14px !important;
}

/* Expanders */
.streamlit-expanderHeader {
    font-size: 14px !important;
    font-weight: 500 !important;
    color: #2D3748 !important;
    background: #F7FAFC !important;
    border-radius: 8px !important;
}

/* Metrics */
.metric-box {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 20px;
    text-align: center;
}

.metric-value {
    font-size: 32px;
    font-weight: 700;
    color: #2D3748;
    line-height: 1;
}

.metric-label {
    font-size: 13px;
    color: #718096;
    margin-top: 6px;
    font-weight: 500;
}

/* Result items */
.result-correct {
    background: #F0FFF4;
    border: 1px solid #C6F6D5;
    border-radius: 8px;
    padding: 14px 16px;
    margin-bottom: 10px;
}

.result-wrong {
    background: #FFF5F5;
    border: 1px solid #FED7D7;
    border-radius: 8px;
    padding: 14px 16px;
    margin-bottom: 10px;
}

/* Log box */
.log-box {
    background: #1A202C;
    color: #A0AEC0;
    border-radius: 8px;
    padding: 16px;
    font-family: 'Courier New', monospace;
    font-size: 12px;
    max-height: 220px;
    overflow-y: auto;
}

/* Progress step */
.step-row {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 12px 0;
    border-bottom: 1px solid #F0F0F0;
}

.step-circle {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 13px;
    font-weight: 600;
    flex-shrink: 0;
}

.step-circle.done { background: #C6F6D5; color: #22543D; }
.step-circle.active { background: #BEE3F8; color: #2A4365; }
.step-circle.pending { background: #EDF2F7; color: #A0AEC0; }

.step-text { font-size: 14px; color: #4A5568; }
.step-text strong { color: #2D3748; }

/* Divider */
.divider { border: none; border-top: 1px solid #E2E8F0; margin: 24px 0; }

/* Tab-like section selector */
.section-tabs {
    display: flex;
    gap: 8px;
    margin-bottom: 24px;
    border-bottom: 2px solid #E2E8F0;
    padding-bottom: 0;
}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════
# SESSION STATE INIT
# ═══════════════════════════════════════════════
def init_state():
    defaults = {
        "page": "home",
        "classroom_courses": [],
        "classroom_connected": False,
        "chosen_course": None,
        "course_materials": [],
        "selected_lectures": [],
        "github_folders": {},
        "github_files_in_folder": {},
        "selected_github_files": [],
        "all_selected_files": [],   # Final list sent to pipeline
        "pipeline_ran": {
            "fetch": False,
            "notes": False,
            "plan": False,
            "analyze": False,
            "quiz": False,
            "score": False,
        },
        "score_result": None,
        "feedback_result": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# ═══════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════
def nav(page):
    st.session_state["page"] = page

def step_done(key):
    """Check if a pipeline step has output."""
    paths = {
        "fetch": "data/chunks",
        "notes": "data/output/notes",
        "plan": "data/output/plan.json",
        "analyze": "data/output/paper_analysis.json",
        "quiz": "data/output/quiz/full_quiz.json",
        "score": "data/output/scores/score_report.json",
    }
    p = paths.get(key, "")
    if not p:
        return False
    if os.path.isdir(p):
        return os.path.exists(p) and len(os.listdir(p)) > 0
    return os.path.exists(p)

def get_repos():
    raw = os.getenv("GITHUB_REPOS", os.getenv("GITHUB_REPO", ""))
    return [r.strip() for r in raw.split(",") if r.strip()]

def log_widget(logs_list):
    """Renders a dark log box."""
    content = "\n".join(logs_list[-40:])
    st.markdown(
        f'<div class="log-box"><pre>{content}</pre></div>',
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════
# SIDEBAR NAVIGATION
# ═══════════════════════════════════════════════
pages = [
    ("home",     "🏠", "Home",          None),
    ("sources",  "📥", "Add Materials", None),
    ("study",    "📝", "Study Notes",   "notes"),
    ("quiz",     "🧠", "Take Quiz",     "quiz"),
    ("results",  "📊", "My Results",    "score"),
]

with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <h1>📚 Study Agent</h1>
        <p>AI-powered exam prep</p>
    </div>
    <div class="nav-section-label">Menu</div>
    """, unsafe_allow_html=True)

    for page_id, icon, label, check_key in pages:
        is_active = st.session_state["page"] == page_id
        badge_html = ""
        if check_key:
            done = step_done(check_key)
            badge_html = f'<span class="nav-badge {"done" if done else ""}">{"✓" if done else "—"}</span>'

        active_class = "active" if is_active else ""
        if st.button(
            f"{icon}  {label}",
            key=f"nav_{page_id}",
            use_container_width=True,
        ):
            nav(page_id)

    st.markdown('<div class="nav-section-label" style="margin-top:auto">Pipeline</div>', unsafe_allow_html=True)

    pipeline_steps = [
        ("fetch",   "Materials fetched"),
        ("notes",   "Notes generated"),
        ("plan",    "Study plan built"),
        ("analyze", "Papers analyzed"),
        ("quiz",    "Quiz generated"),
        ("score",   "Quiz attempted"),
    ]
    for key, label in pipeline_steps:
        done = step_done(key)
        icon = "✅" if done else "⬜"
        st.markdown(
            f'<div style="padding:4px 24px;font-size:12px;color:{"#68D391" if done else "rgba(255,255,255,0.3)"};">'
            f'{icon} {label}</div>',
            unsafe_allow_html=True,
        )


# ═══════════════════════════════════════════════
# PAGE: HOME
# ═══════════════════════════════════════════════
if st.session_state["page"] == "home":
    st.markdown("""
    <div class="page-header">
        <h2>Welcome to Study Agent</h2>
        <p>Your AI-powered exam preparation companion. Follow the steps below to get started.</p>
    </div>
    """, unsafe_allow_html=True)

    # How it works
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🗺️ How it works</div>', unsafe_allow_html=True)

    steps_info = [
        ("fetch",   "1", "Add Materials",   "Connect Google Classroom or GitHub, pick your lectures and past papers"),
        ("notes",   "2", "Generate Notes",  "AI reads your materials and creates structured study notes"),
        ("plan",    "3", "Study Plan",      "AI identifies topics, ranks by importance, estimates study time"),
        ("analyze", "4", "Paper Analysis",  "AI scans past papers and finds what topics come up most"),
        ("quiz",    "5", "Take Quiz",       "AI generates targeted MCQ quiz based on your notes and past papers"),
        ("score",   "6", "Get Results",     "Submit answers and get instant feedback with per-question explanations"),
    ]

    for key, num, title, desc in steps_info:
        done = step_done(key)
        state_class = "done" if done else "pending"
        st.markdown(f"""
        <div class="step-row">
            <div class="step-circle {state_class}">{("✓" if done else num)}</div>
            <div class="step-text"><strong>{title}</strong><br><span style="font-size:13px;color:#718096">{desc}</span></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Quick actions
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="card" style="text-align:center">', unsafe_allow_html=True)
        st.markdown("### 📥\n**Start here**\nAdd your lecture materials and past papers")
        if st.button("Add Materials", type="primary", use_container_width=True, key="home_sources"):
            nav("sources")
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="card" style="text-align:center">', unsafe_allow_html=True)
        st.markdown("### 📝\n**Review notes**\nRead AI-generated study notes by topic")
        if st.button("Study Notes", type="secondary", use_container_width=True, key="home_study"):
            nav("study")
        st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="card" style="text-align:center">', unsafe_allow_html=True)
        st.markdown("### 🧠\n**Test yourself**\nAttempt AI-generated quiz and get scored")
        if st.button("Take Quiz", type="secondary", use_container_width=True, key="home_quiz"):
            nav("quiz")
        st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════
# PAGE: SOURCES (Add Materials)
# ═══════════════════════════════════════════════
elif st.session_state["page"] == "sources":
    st.markdown("""
    <div class="page-header">
        <h2>📥 Add Study Materials</h2>
        <p>Choose where to get your lectures and past papers from. You can combine multiple sources.</p>
    </div>
    """, unsafe_allow_html=True)
if step_done("fetch"):
        st.info(
            "✓ You already processed materials. "
            "You can add more below, or clear everything and start fresh."
        )
        if st.button("🗑️ Clear all processed data and start over", key="full_reset"):
            import shutil
            for folder in ["data/chunks", "data/output"]:
                if os.path.exists(folder):
                    shutil.rmtree(folder)
            st.session_state["selected_lectures"] = []
            st.session_state["selected_github_files"] = []
            st.session_state["classroom_connected"] = False
            st.session_state["classroom_courses"] = []
            st.session_state["chosen_course"] = None
            st.session_state["course_materials"] = []
            st.session_state["github_folders"] = {}
            st.session_state["github_files_in_folder"] = {}
            st.success("Everything cleared. Select your materials again.")
            st.rerun()
    # ── SOURCE 1: GOOGLE CLASSROOM ──
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🎓 Google Classroom</div>', unsafe_allow_html=True)

    if not os.path.exists("credentials.json"):
        st.warning(
            "**Setup required before connecting Classroom.**\n\n"
            "1. Go to **console.cloud.google.com**\n"
            "2. Create a project → Enable **Google Classroom API** and **Google Drive API**\n"
            "3. Go to **Credentials → Create OAuth client ID** → Choose **Desktop app**\n"
            "4. Download the JSON file → rename it to **credentials.json**\n"
            "5. Place it in your project folder alongside app.py"
        )
    else:
        # Always allow connecting as any Google account
        col_a, col_b = st.columns([2, 1])
        with col_a:
            st.info(
                "Click **Connect Classroom** to sign in with any Google account. "
                "A browser window will open for login. "
                "Each user logs in with their own Gmail and sees their own courses."
            )
        with col_b:
            if st.button("🔗 Connect Classroom", type="primary", key="connect_btn"):
                # Force fresh login by deleting old token
                if os.path.exists("token.json"):
                    os.remove("token.json")
                with st.spinner("Opening browser for login..."):
                    try:
                        from tools.classroom_tool import list_enrolled_courses
                        courses = list_enrolled_courses()
                        st.session_state["classroom_courses"] = courses
                        st.session_state["classroom_connected"] = True
                        st.session_state["chosen_course"] = None
                        st.session_state["course_materials"] = []
                        st.session_state["selected_lectures"] = []
                        if courses:
                            st.success(f"Connected! Found {len(courses)} active course(s).")
                        else:
                            st.warning("No active courses found in this account.")
                    except Exception as e:
                        st.error(f"Connection failed: {e}")
                        st.info("Make sure credentials.json is in your project folder and Google Cloud OAuth is set up.")

        # Course selector
        if st.session_state["classroom_connected"] and st.session_state["classroom_courses"]:
            courses = st.session_state["classroom_courses"]

            st.markdown("---")
            st.markdown("**Step 1 — Select a course:**")

            course_options = ["— choose a course —"] + [
                f"{c['name']}" + (f" ({c['section']})" if c.get("section") else "")
                for c in courses
            ]

            chosen_label = st.selectbox(
                "Your enrolled courses:",
                options=course_options,
                key="course_dropdown",
                label_visibility="collapsed",
            )

            if chosen_label != "— choose a course —":
                idx = course_options.index(chosen_label) - 1
                chosen_course = courses[idx]

                # Load materials button
                if st.button(
                    f"📋 Load lectures from  '{chosen_course['name']}'",
                    key="load_materials_btn",
                ):
                    with st.spinner("Loading all materials from this course..."):
                        try:
                            from tools.classroom_tool import list_materials_in_course
                            materials = list_materials_in_course(chosen_course["id"])
                            st.session_state["course_materials"] = materials
                            st.session_state["chosen_course"] = chosen_course
                            st.session_state["selected_lectures"] = []
                            if materials:
                                st.success(f"Found {len(materials)} lecture file(s).")
                            else:
                                st.warning(
                                    "No downloadable files found. "
                                    "Files must be PDF, PPTX, or DOCX attached to materials or assignments."
                                )
                        except Exception as e:
                            st.error(f"Error loading materials: {e}")

                # Material picker
                if (
                    st.session_state["course_materials"]
                    and st.session_state.get("chosen_course", {}).get("id") == chosen_course["id"]
                ):
                    materials = st.session_state["course_materials"]

                    st.markdown("---")
                    st.markdown("**Step 2 — Select which lectures to use:**")

                    select_all_lectures = st.checkbox(
                        f"Select all {len(materials)} lecture(s)",
                        key="select_all_lec",
                    )

                    selected = []
                    for mat in materials:
                        parent = mat.get("parent_title", "")
                        label = mat["title"]
                        if parent:
                            label += f"  —  *{parent[:50]}*"

                        checked = select_all_lectures or st.checkbox(
                            label, key=f"lec_{mat['id']}"
                        )
                        if checked:
                            selected.append(mat)

                    st.session_state["selected_lectures"] = selected

                    if selected:
                        st.success(f"✓ {len(selected)} lecture(s) selected")

    st.markdown('</div>', unsafe_allow_html=True)

    # ── SOURCE 2: GITHUB ──
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📁 GitHub Past Papers</div>', unsafe_allow_html=True)

    repos = get_repos()
    if not repos:
        st.warning(
            "No GitHub repos configured.\n\n"
            "Add `GITHUB_REPOS=username/repo1,username/repo2` to your `.env` file."
        )
    else:
        col_r1, col_r2 = st.columns([2, 1])
        with col_r1:
            selected_repo = st.selectbox(
                "Select repository:",
                options=["— choose a repo —"] + repos,
                key="repo_dropdown",
            )
        with col_r2:
            if selected_repo != "— choose a repo —":
                if st.button("📂 Load folders", key="load_folders_btn", type="primary"):
                    with st.spinner(f"Loading {selected_repo}..."):
                        try:
                            from tools.github_tool import list_folders_in_repo
                            folders, root_files = list_folders_in_repo(selected_repo)
                            st.session_state["github_folders"][selected_repo] = folders
                            st.session_state["github_root_files"] = root_files
                            st.session_state["github_files_in_folder"] = {}
                            st.session_state["selected_github_files"] = []
                            st.success(f"Found {len(folders)} folder(s)")
                        except Exception as e:
                            st.error(f"Error: {e}")

        if selected_repo != "— choose a repo —" and selected_repo in st.session_state["github_folders"]:
            folders = st.session_state["github_folders"][selected_repo]
            root_files = st.session_state.get("github_root_files", [])

            if folders:
                st.markdown("---")
                st.markdown("**Step 1 — Select a subject folder:**")

                folder_names = ["— choose a folder —"] + [f["name"] for f in folders]
                chosen_folder_name = st.selectbox(
                    "Subject folders:",
                    options=folder_names,
                    key="folder_dropdown",
                    label_visibility="collapsed",
                )

                if chosen_folder_name != "— choose a folder —":
                    folder_info = next(f for f in folders if f["name"] == chosen_folder_name)

                    if st.button(
                        f"📋 Load files in '{chosen_folder_name}'",
                        key="load_files_btn",
                    ):
                        with st.spinner("Loading files..."):
                            try:
                                from tools.github_tool import list_files_in_path
                                files = list_files_in_path(selected_repo, folder_info["path"])
                                st.session_state["github_files_in_folder"][chosen_folder_name] = files
                                st.session_state["selected_github_files"] = []
                                st.success(f"Found {len(files)} file(s)")
                            except Exception as e:
                                st.error(f"Error: {e}")

                    folder_files = st.session_state["github_files_in_folder"].get(chosen_folder_name, [])

                    if folder_files:
                        st.markdown("---")
                        st.markdown("**Step 2 — Select which papers to use:**")

                        select_all_gh = st.checkbox(
                            f"Select all {len(folder_files)} file(s)",
                            key="select_all_gh",
                        )

                        selected_gh = []
                        for fi in folder_files:
                            size_str = f"{fi.get('size_kb', '?')} KB"
                            label = f"{fi['name']}  ({size_str})"
                            checked = select_all_gh or st.checkbox(
                                label, key=f"ghf_{fi['path']}"
                            )
                            if checked:
                                selected_gh.append(fi)

                        st.session_state["selected_github_files"] = selected_gh

                        if selected_gh:
                            st.success(f"✓ {len(selected_gh)} file(s) selected")

            # Root-level files (not in any folder)
            if root_files:
                st.markdown("---")
                st.markdown("**Root-level files:**")
                for fi in root_files:
                    if st.checkbox(fi["name"], key=f"root_{fi['path']}"):
                        existing = st.session_state.get("selected_github_files", [])
                        if fi not in existing:
                            existing.append(fi)
                        st.session_state["selected_github_files"] = existing

    st.markdown('</div>', unsafe_allow_html=True)

    # ── SOURCE 3: MANUAL UPLOAD ──
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📤 Upload Files Manually</div>', unsafe_allow_html=True)
    st.markdown("Don't have Classroom or GitHub? Upload your files directly.")

    uploaded_files = st.file_uploader(
        "Upload PDF, PPTX, or DOCX files",
        accept_multiple_files=True,
        type=["pdf", "pptx", "docx", "txt"],
        label_visibility="collapsed",
    )
    if uploaded_files:
        os.makedirs("data/raw", exist_ok=True)
        for f in uploaded_files:
            path = os.path.join("data/raw", f.name)
            with open(path, "wb") as out:
                out.write(f.getbuffer())
        st.success(f"✓ {len(uploaded_files)} file(s) ready")

    st.markdown('</div>', unsafe_allow_html=True)

    # ── SELECTION SUMMARY ──
    selected_lectures = st.session_state.get("selected_lectures", [])
    selected_github = st.session_state.get("selected_github_files", [])
    uploaded_count = len(uploaded_files) if uploaded_files else 0
    total_selected = len(selected_lectures) + len(selected_github) + uploaded_count

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📋 Selected Materials Summary</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Classroom lectures", len(selected_lectures))
    col2.metric("GitHub papers", len(selected_github))
    col3.metric("Uploaded files", uploaded_count)
    col4.metric("Total selected", total_selected)

   if total_selected == 0:
    st.warning("No materials selected yet. Select files above, then click Process.")
else:
    st.success(f"✓ {total_selected} file(s) ready to process")

    col_proc1, col_proc2 = st.columns([3, 1])

    with col_proc2:
        if st.button("🔄 Clear & Start Over", key="clear_selection", use_container_width=True):
            # Clear all selections
            st.session_state["selected_lectures"] = []
            st.session_state["selected_github_files"] = []
            st.session_state["classroom_connected"] = False
            st.session_state["classroom_courses"] = []
            st.session_state["chosen_course"] = None
            st.session_state["course_materials"] = []
            st.session_state["github_folders"] = {}
            st.session_state["github_files_in_folder"] = {}
            st.session_state["github_root_files"] = []

            # Also clear old chunks so pipeline resets
            import shutil
            if os.path.exists("data/chunks"):
                shutil.rmtree("data/chunks")
                os.makedirs("data/chunks")

            st.success("Selection cleared. Choose your materials again.")
            st.rerun()

    with col_proc1:
        if st.button("⚡ Process Selected Materials", type="primary", use_container_width=True, key="process_btn"):
            log_lines = []
            log_placeholder = st.empty()

            def log_cb(msg):
                log_lines.append(str(msg))
                log_widget(log_lines)

            with st.spinner("Processing your selected materials..."):
                try:
                    os.makedirs("data/raw", exist_ok=True)
                    os.makedirs("data/chunks", exist_ok=True)

                    # Download Classroom lectures
                    classroom_paths = []
                    if selected_lectures:
                        log_cb(f"Downloading {len(selected_lectures)} lecture(s) from Classroom...")
                        from tools.classroom_tool import download_selected_materials
                        classroom_paths = download_selected_materials(
                            selected_lectures,
                            "data/raw",
                            progress_callback=log_cb,
                        )

                    # Download GitHub files
                    github_paths = []
                    if selected_github:
                        log_cb(f"Downloading {len(selected_github)} file(s) from GitHub...")
                        from tools.github_tool import download_selected_files
                        github_paths = download_selected_files(
                            selected_github,
                            "data/raw",
                            progress_callback=log_cb,
                        )

                    # Combine all paths — only selected files
                    # Also include any manually uploaded files
                    all_paths = list(set(classroom_paths + github_paths))

                    # Add uploaded files
                    if uploaded_files:
                        for f in uploaded_files:
                            p = os.path.join("data/raw", f.name)
                            if p not in all_paths and os.path.exists(p):
                                all_paths.append(p)

                    if not all_paths:
                        st.error("No files could be downloaded. Check your connections.")
                    else:
                        log_cb(f"\nProcessing {len(all_paths)} file(s) into chunks...")

                        # Process ONLY these specific files — not everything in raw/
                        from tools.pdf_tool import process_pdf, process_text
                        from tools.file_converter import convert_file

                        os.makedirs("data/chunks", exist_ok=True)
                        chunk_files = []

                        for file_path in all_paths:
                            ext = os.path.splitext(file_path)[1].lower()
                            filename = os.path.basename(file_path).rsplit(".", 1)[0]
                            try:
                                if ext == ".pdf":
                                    result = process_pdf(file_path, "data/chunks")
                                elif ext in (".pptx", ".ppt", ".docx"):
                                    text = convert_file(file_path)
                                    result = process_text(text, filename, "data/chunks") if text else None
                                elif ext == ".txt":
                                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                                        text = f.read()
                                    result = process_text(text, filename, "data/chunks")
                                else:
                                    result = None

                                if result:
                                    chunk_files.append(result)
                                    log_cb(f"  ✓ Processed: {filename}")
                                else:
                                    log_cb(f"  ✗ Skipped: {filename}")
                            except Exception as e:
                                log_cb(f"  ✗ Error on {filename}: {e}")

                        if chunk_files:
                            st.session_state["pipeline_ran"]["fetch"] = True
                            st.success(
                                f"✅ Done! {len(chunk_files)} file(s) processed. "
                                "Go to **Study Notes** to generate your notes."
                            )
                            st.balloons()
                        else:
                            st.error("Processing failed. Check file formats.")

                except Exception as e:
                    st.error(f"Error: {e}")
                    import traceback
                    st.code(traceback.format_exc())

    st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════
# PAGE: STUDY (Notes + Plan + Analysis)
# ═══════════════════════════════════════════════
elif st.session_state["page"] == "study":
    st.markdown("""
    <div class="page-header">
        <h2>📝 Study Materials</h2>
        <p>Generate and read your AI-powered study notes, study plan, and past paper analysis.</p>
    </div>
    """, unsafe_allow_html=True)

    has_chunks = step_done("fetch")

    if not has_chunks:
        st.warning("You haven't processed any materials yet. Go to **Add Materials** first.")
        if st.button("← Go to Add Materials"):
            nav("sources")
    else:
        chunk_count = len([f for f in os.listdir("data/chunks") if f.endswith(".json")]) if os.path.exists("data/chunks") else 0

        # ── STEP A: GENERATE NOTES ──
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📄 Study Notes</div>', unsafe_allow_html=True)

        if step_done("notes"):
            notes_count = len(os.listdir("data/output/notes")) if os.path.exists("data/output/notes") else 0
            st.success(f"✓ {notes_count} notes file(s) already generated.")
            col_nb1, col_nb2 = st.columns(2)
            with col_nb1:
                if st.button("🔄 Regenerate Notes", key="regen_notes"):
                    _do_gen_notes = True
                else:
                    _do_gen_notes = False
        else:
            st.info(f"{chunk_count} file(s) ready. Click to generate notes.")
            _do_gen_notes = st.button("📝 Generate Study Notes", type="primary", key="gen_notes")

        if _do_gen_notes:
            log_lines = []
            log_placeholder = st.empty()

            with st.spinner("Generating study notes..."):
                try:
                    from agents.notes_agent import run_notes_agent
                    os.makedirs("data/output/notes", exist_ok=True)
                    notes = run_notes_agent(
                        chunks_dir="data/chunks",
                        notes_dir="data/output/notes",
                        progress_callback=lambda m: log_lines.append(str(m)),
                    )
                    if notes:
                        st.success(f"✅ {len(notes)} notes file(s) created!")
                    else:
                        st.error("Notes generation failed.")
                except Exception as e:
                    st.error(f"Error: {e}")

        # Show notes
        if step_done("notes"):
            st.markdown("---")
            notes_files = [f for f in os.listdir("data/output/notes") if f.endswith(".md")]
            if notes_files:
                selected_note = st.selectbox(
                    "Read notes for:",
                    options=notes_files,
                    format_func=lambda x: x.replace("_notes.md", "").replace("_", " "),
                    key="notes_reader",
                )
                if selected_note:
                    with open(os.path.join("data/output/notes", selected_note), "r", encoding="utf-8") as f:
                        st.markdown(f.read())

        st.markdown('</div>', unsafe_allow_html=True)

        # ── STEP B: STUDY PLAN ──
        if step_done("notes"):
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">🗂️ Study Plan</div>', unsafe_allow_html=True)

            if step_done("plan"):
                st.success("✓ Study plan already built.")
                _do_plan = st.button("🔄 Rebuild Plan", key="regen_plan")
            else:
                _do_plan = st.button("🗂️ Build Study Plan", type="primary", key="build_plan")

            if _do_plan:
                with st.spinner("Building your personalised study plan..."):
                    try:
                        from agents.planner_agent import run_planner_agent
                        result = run_planner_agent(
                            notes_dir="data/output/notes",
                            output_path="data/output/plan.json",
                        )
                        if result:
                            st.success("✅ Study plan created!")
                        else:
                            st.error("Planning failed.")
                    except Exception as e:
                        st.error(f"Error: {e}")

            if step_done("plan"):
                with open("data/output/plan.json") as f:
                    plan = json.load(f)
                topics = plan.get("topics", [])

                st.markdown("---")
                c1, c2, c3 = st.columns(3)
                c1.metric("Topics found", len(topics))
                c2.metric("Total study time", plan.get("total_study_time", "N/A"))
                c3.metric("High priority", len([t for t in topics if t.get("priority") == "high"]))

                st.markdown("#### Your study order")
                for t in sorted(topics, key=lambda x: x.get("study_order", 99)):
                    p = t.get("priority", "medium")
                    icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(p, "⚪")
                    with st.expander(
                        f"{icon}  {t.get('study_order')}. {t.get('name')} — {t.get('estimated_study_time','?')}"
                    ):
                        st.write(f"**Priority:** {p.upper()}   |   **Exam weight:** {t.get('exam_weight','N/A')}")
                        concepts = t.get("key_concepts", [])
                        if concepts:
                            st.write("**Key concepts:**  " + ",  ".join(concepts))

            st.markdown('</div>', unsafe_allow_html=True)

        # ── STEP C: PAPER ANALYSIS ──
        if step_done("notes"):
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">🔍 Past Paper Analysis</div>', unsafe_allow_html=True)

            if step_done("analyze"):
                st.success("✓ Past paper analysis already done.")
                _do_analyze = st.button("🔄 Re-analyze", key="regen_analyze")
            else:
                _do_analyze = st.button("🔍 Analyze Past Papers", type="primary", key="do_analyze")

            if _do_analyze:
                with st.spinner("Scanning past papers for patterns..."):
                    try:
                        from agents.paper_analyzer_agent import run_paper_analyzer_agent
                        result = run_paper_analyzer_agent(
                            chunks_dir="data/chunks",
                            output_path="data/output/paper_analysis.json",
                        )
                        if result:
                            st.success("✅ Analysis complete!")
                        else:
                            st.error("Analysis failed.")
                    except Exception as e:
                        st.error(f"Error: {e}")

            if step_done("analyze"):
                with open("data/output/paper_analysis.json") as f:
                    analysis = json.load(f)

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Top topics in past papers:**")
                    top_topics = analysis.get("top_topics", [])[:8]
                    if top_topics:
                        import pandas as pd
                        df = pd.DataFrame(top_topics)
                        st.bar_chart(df.set_index("topic")["frequency"])

                with col2:
                    st.markdown("**High frequency terms:**")
                    for t in analysis.get("high_frequency_terms", [])[:8]:
                        st.write(f"- **{t['term']}** ({t['count']}x)")

                st.markdown("**Recommended focus areas:**")
                focus = analysis.get("recommended_focus", [])
                for i, f in enumerate(focus, 1):
                    st.write(f"{i}. {f}")

            st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════
# PAGE: QUIZ
# ═══════════════════════════════════════════════
elif st.session_state["page"] == "quiz":
    st.markdown("""
    <div class="page-header">
        <h2>🧠 Take a Quiz</h2>
        <p>Test your knowledge with AI-generated questions based on your study materials.</p>
    </div>
    """, unsafe_allow_html=True)

    has_notes = step_done("notes")

    if not has_notes:
        st.warning("Generate study notes first. Go to **Study Notes**.")
        if st.button("← Go to Study Notes"):
            nav("study")
    else:
        # Generate quiz section
        if not step_done("quiz"):
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">⚡ Generate Quiz</div>', unsafe_allow_html=True)
            st.info(
                "Your quiz will be generated based on your study notes, study plan, "
                "and past paper patterns. This gives you the most relevant questions."
            )

            if st.button("🧠 Generate Quiz Now", type="primary", key="gen_quiz"):
                with st.spinner("Generating your personalised quiz..."):
                    try:
                        from agents.quiz_agent import run_quiz_agent
                        os.makedirs("data/output/quiz", exist_ok=True)
                        results = run_quiz_agent(
                            notes_dir="data/output/notes",
                            plan_path="data/output/plan.json",
                            analysis_path="data/output/paper_analysis.json",
                            quiz_dir="data/output/quiz",
                        )
                        if results:
                            st.success("✅ Quiz ready! Scroll down to attempt it.")
                            st.rerun()
                        else:
                            st.error("Quiz generation failed.")
                    except Exception as e:
                        st.error(f"Error: {e}")
            st.markdown('</div>', unsafe_allow_html=True)

        # Attempt quiz
        if step_done("quiz"):
            with open("data/output/quiz/full_quiz.json") as f:
                quiz = json.load(f)

            questions = quiz.get("questions", [])

            if not questions:
                st.error("Quiz file is empty. Try regenerating.")
            else:
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.markdown(f'<div class="card">', unsafe_allow_html=True)
                    st.markdown(
                        f'<div class="card-title">📋 Quiz — {len(questions)} Questions</div>',
                        unsafe_allow_html=True,
                    )

                with col_b:
                    if st.button("🔄 New Quiz", key="regen_quiz_btn"):
                        with st.spinner("Generating new quiz..."):
                            try:
                                from agents.quiz_agent import run_quiz_agent
                                os.makedirs("data/output/quiz", exist_ok=True)
                                run_quiz_agent(
                                    notes_dir="data/output/notes",
                                    plan_path="data/output/plan.json",
                                    analysis_path="data/output/paper_analysis.json",
                                    quiz_dir="data/output/quiz",
                                )
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")

                user_answers = {}

                with st.form("quiz_form"):
                    for i, q in enumerate(questions, 1):
                        diff = q.get("difficulty", "?")
                        topic = q.get("topic", "")
                        diff_color = {"easy": "#48BB78", "medium": "#ECC94B", "hard": "#FC8181"}.get(diff, "#A0AEC0")

                        st.markdown(
                            f'<div style="margin-bottom:4px">'
                            f'<span style="font-size:13px;color:{diff_color};font-weight:600">'
                            f'{diff.upper()}</span>'
                            f'<span style="font-size:13px;color:#A0AEC0;margin-left:10px">{topic}</span>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )
                        st.markdown(f"**Q{i}.** {q['question']}")

                        options = q["options"]
                        choice = st.radio(
                            f"q{i}",
                            options=list(options.keys()),
                            format_func=lambda x, o=options: f"{x}.  {o[x]}",
                            horizontal=True,
                            key=f"ans_{i}",
                            label_visibility="collapsed",
                        )
                        user_answers[i] = choice
                        st.markdown('<hr style="border-color:#F0F0F0;margin:16px 0">', unsafe_allow_html=True)

                    submitted = st.form_submit_button(
                        "✅  Submit Quiz & See Results",
                        type="primary",
                        use_container_width=True,
                    )

                st.markdown('</div>', unsafe_allow_html=True)

                if submitted:
                    with st.spinner("Evaluating your answers..."):
                        try:
                            from agents.scoring_agent import run_scoring_agent
                            os.makedirs("data/output/scores", exist_ok=True)
                            os.makedirs("data/output/feedback", exist_ok=True)

                            result = run_scoring_agent(
                                quiz_dir="data/output/quiz",
                                scores_dir="data/output/scores",
                                feedback_dir="data/output/feedback",
                                user_answers=user_answers,
                            )

                            if result:
                                st.session_state["score_result"] = result[0]
                                st.session_state["feedback_result"] = result[1]
                                st.success("✅ Submitted! Go to **My Results** to see your score.")
                                if st.button("📊 View My Results →", type="primary"):
                                    nav("results")
                            else:
                                st.error("Scoring failed.")
                        except Exception as e:
                            st.error(f"Error: {e}")


# ═══════════════════════════════════════════════
# PAGE: RESULTS
# ═══════════════════════════════════════════════
elif st.session_state["page"] == "results":
    st.markdown("""
    <div class="page-header">
        <h2>📊 My Results</h2>
        <p>See your quiz score, per-question feedback, and topics to revise.</p>
    </div>
    """, unsafe_allow_html=True)

    if not step_done("score"):
        st.warning("You haven't attempted a quiz yet. Go to **Take Quiz** first.")
        if st.button("← Take Quiz"):
            nav("quiz")
    else:
        # Load results
        with open("data/output/scores/score_report.json") as f:
            score_report = json.load(f)
        with open("data/output/feedback/feedback.json") as f:
            feedback_out = json.load(f)

        score = score_report["score"]
        total = score_report["total"]
        percent = score_report["percent"]
        grade = score_report["grade"]
        weak_topics = score_report.get("weak_topics", [])

        # Score banner
        grade_color = {
            "Excellent": "#48BB78",
            "Good": "#63B3ED",
            "Needs Work": "#ECC94B",
            "Revise This Topic": "#FC8181",
        }.get(grade, "#A0AEC0")

        st.markdown(
            f'<div style="background:linear-gradient(135deg,{grade_color}22,{grade_color}11);'
            f'border:2px solid {grade_color}44;border-radius:16px;padding:32px;text-align:center;margin-bottom:24px">'
            f'<div style="font-size:48px;font-weight:800;color:{grade_color}">{percent}%</div>'
            f'<div style="font-size:20px;font-weight:600;color:#2D3748;margin-top:8px">{grade}</div>'
            f'<div style="font-size:15px;color:#718096;margin-top:4px">Score: {score} / {total}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Metrics
        correct = score
        wrong = total - score
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Questions", total)
        c2.metric("Correct", correct)
        c3.metric("Wrong", wrong)
        c4.metric("Score %", f"{percent}%")

        # Per-question feedback
        st.markdown("---")
        st.markdown("### Question-by-question review")

        results = score_report.get("results", [])
        feedbacks = feedback_out.get("per_question_feedback", [])

        for res, fb in zip(results, feedbacks):
            is_correct = res["is_correct"]
            box_class = "result-correct" if is_correct else "result-wrong"
            icon = "✅" if is_correct else "❌"
            diff = res.get("difficulty", "?")

            with st.expander(
                f"{icon}  Q{res['q_number']}  [{diff}]  —  {res['question'][:75]}..."
            ):
                col_a, col_b = st.columns(2)
                col_a.markdown(f"**Your answer:** {res['user_answer']}")
                col_b.markdown(f"**Correct answer:** {res['correct_answer']}")

                if is_correct:
                    st.success(fb["feedback"])
                else:
                    st.error(fb["feedback"])

                topic = res.get("topic", "")
                if topic:
                    st.caption(f"Topic: {topic}")

        # Topics to revise
        if weak_topics:
            st.markdown("---")
            st.markdown("### 📚 Topics to revise")
            st.info(
                "You got questions wrong in these topics. "
                "Go back to Study Notes to review them."
            )
            for t in set(weak_topics):
                st.markdown(f"- **{t}**")

            if st.button("📝 Back to Study Notes", type="primary"):
                nav("study")

        # Retake
        st.markdown("---")
        if st.button("🔄 Retake Quiz", use_container_width=True):
            nav("quiz")