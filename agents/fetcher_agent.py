import os
from tools.pdf_tool import process_pdf, process_text
from tools.file_converter import convert_file
from tools.github_tool import fetch_all_from_github


def run_fetcher_agent(
    raw_dir,
    chunks_dir,
    github_repo=None,
    selected_courses=None,
    token_path="token.json",
    progress_callback=None,
):
    def log(msg):
        print(msg)
        if progress_callback:
            progress_callback(msg)

    log("=" * 50)
    log("AGENT 1: FETCHER AGENT")
    log("=" * 50)

    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(chunks_dir, exist_ok=True)
    all_file_paths = []

    # Step 1: Google Classroom
    if not selected_courses:
        from tools.classroom_tool import list_enrolled_courses
        print("\nNo courses provided. Fetching your Google Classroom courses...")
        courses = list_enrolled_courses(token_path)
        
        if not courses:
            log(" ✗ No active courses found in your Classroom.")
        else:
            for i, c in enumerate(courses):
                print(f"  [{i}] {c['name']}")
            choice = input("\nEnter the numbers of the courses to fetch (comma separated, e.g., 0,1) or press Enter to skip: ")
            
            if choice.strip():
                indices = [int(x.strip()) for x in choice.split(",")]
                selected_courses = [courses[i] for i in indices if i < len(courses)]
    if selected_courses:
        log("\n[Step 1] Fetching from Google Classroom...")
        try:
            from tools.classroom_tool import fetch_materials_from_course
            for course in selected_courses:
                log(f"  Course: {course['name']}")
                files = fetch_materials_from_course(
                    course["id"], course["name"], raw_dir,
                    token_path=token_path,
                    progress_callback=progress_callback,
                )
                all_file_paths.extend(files)
        except Exception as e:
            log(f"  ✗ Classroom error: {e}")
    else:
        log("\n[Step 1] No Classroom course selected. Skipping.")

    # Step 2: GitHub past papers
    log("\n[Step 2] Checking GitHub...")
    try:
        github_files = fetch_all_from_github(
            raw_dir, repo=github_repo, progress_callback=progress_callback
        )
        all_file_paths.extend(github_files)
    except Exception as e:
        log(f"  ✗ GitHub error: {e}")

    # Step 3: Local fallback
    log("\n[Step 3] Checking local data/raw/...")
    supported = (".pdf", ".pptx", ".docx", ".txt", ".ppt")
    for filename in os.listdir(raw_dir):
        if filename.lower().endswith(supported):
            full_path = os.path.join(raw_dir, filename)
            if full_path not in all_file_paths:
                all_file_paths.append(full_path)
                log(f"  Found local: {filename}")

    # Deduplicate
    seen = set()
    unique = []
    for p in all_file_paths:
        if p not in seen:
            seen.add(p)
            unique.append(p)
    all_file_paths = unique

    if not all_file_paths:
        log("\n⚠ No files found. Add files to data/raw/ or select a course.")
        return []

    # Step 4: Convert and chunk
    log(f"\n[Step 4] Processing {len(all_file_paths)} file(s)...")
    chunk_files = []

    for file_path in all_file_paths:
        ext = os.path.splitext(file_path)[1].lower()
        filename = os.path.basename(file_path).rsplit(".", 1)[0]
        try:
            if ext == ".pdf":
                result = process_pdf(file_path, chunks_dir)
            elif ext in (".pptx", ".ppt", ".docx"):
                text = convert_file(file_path)
                result = process_text(text, filename, chunks_dir) if text else None
            elif ext == ".txt":
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
                result = process_text(text, filename, chunks_dir)
            else:
                result = None
            if result:
                chunk_files.append(result)
        except Exception as e:
            log(f"  ✗ Error on {filename}: {e}")

    log(f"\n✓ Done! {len(chunk_files)}/{len(all_file_paths)} file(s) chunked.")
    return chunk_files