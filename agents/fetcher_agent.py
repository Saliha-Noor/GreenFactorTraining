import os
from tools.github_tool import fetch_all_from_github
from tools.pdf_tool import process_pdf, process_text
from tools.file_converter import convert_file


def run_fetcher_agent(raw_dir, chunks_dir, github_repo=None):
    print("\n" + "="*50)
    print("AGENT 1: FETCHER AGENT (Tool Use Pattern)")
    print("="*50)

    all_file_paths = []

    # TOOL 1: GitHub
    print("\nStep 1: Checking GitHub for past papers...")
    if github_repo:
        github_pdfs = fetch_all_from_github(raw_dir, github_repo)
        all_file_paths.extend(github_pdfs)
        print(f"  GitHub gave us {len(github_pdfs)} file(s)")
    else:
        print("  No GitHub repo given. Skipping GitHub.")

    # TOOL 2: Local files
    print("\nStep 2: Checking local data/raw/ folder...")
    supported = (".pdf", ".pptx", ".docx", ".txt")
    for filename in os.listdir(raw_dir):
        if filename.lower().endswith(supported):
            full_path = os.path.join(raw_dir, filename)
            if full_path not in all_file_paths:
                all_file_paths.append(full_path)
                print(f"  Found: {filename}")

    if not all_file_paths:
        print("\nNo files found! Add files to data/raw/ and run again.")
        return []

    print(f"\nTotal files to process: {len(all_file_paths)}")

    # TOOL 3: Process each file
    print("\nStep 3: Converting and chunking all files...")
    chunk_files = []

    for file_path in all_file_paths:
        ext = os.path.splitext(file_path)[1].lower()
        filename = os.path.basename(file_path).rsplit(".", 1)[0]

        if ext == ".pdf":
            result = process_pdf(file_path, chunks_dir)
        elif ext in (".pptx", ".docx"):
            text = convert_file(file_path)
            if text:
                result = process_text(text, filename, chunks_dir)
            else:
                result = None
        elif ext == ".txt":
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
            result = process_text(text, filename, chunks_dir)
        else:
            result = None

        if result:
            chunk_files.append(result)
        else:
            print(f"  Skipped: {filename}")

    print(f"\nFetcher Agent done!")
    print(f"  Processed: {len(chunk_files)} files")
    print(f"  Chunks saved to: {chunks_dir}/")
    return chunk_files