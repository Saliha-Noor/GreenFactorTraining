import os
import requests
from dotenv import load_dotenv

load_dotenv()

SUPPORTED = (".pdf", ".pptx", ".docx", ".txt")


def _headers():
    token = os.getenv("GITHUB_TOKEN", "")
    h = {"Accept": "application/vnd.github.v3+json"}
    if token:
        h["Authorization"] = f"token {token}"
    return h


def get_all_repos():
    """Returns list of repos from GITHUB_REPOS env variable."""
    repos_env = os.getenv("GITHUB_REPOS", os.getenv("GITHUB_REPO", ""))
    if not repos_env:
        return []
    return [r.strip() for r in repos_env.split(",") if r.strip()]


def list_folders_in_repo(repo):
    """Returns list of top-level folders in a repo."""
    url = f"https://api.github.com/repos/{repo}/contents"
    try:
        resp = requests.get(url, headers=_headers(), timeout=15)
    except Exception as e:
        print(f"  GitHub error: {e}")
        return []
    if resp.status_code != 200:
        print(f"  GitHub {resp.status_code}: {resp.text[:80]}")
        return []

    folders = []
    files = []
    for item in resp.json():
        if item["type"] == "dir":
            folders.append({
                "name": item["name"],
                "path": item["path"],
                "repo": repo,
            })
        elif item["type"] == "file":
            ext = os.path.splitext(item["name"])[1].lower()
            if ext in SUPPORTED:
                files.append({
                    "name": item["name"],
                    "path": item["path"],
                    "download_url": item["download_url"],
                    "repo": repo,
                    "type": "file",
                })
    return folders, files


def list_files_in_path(repo, path=""):
    """Returns all supported files inside a specific folder path."""
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    try:
        resp = requests.get(url, headers=_headers(), timeout=15)
    except Exception as e:
        print(f"  GitHub error: {e}")
        return []
    if resp.status_code != 200:
        print(f"  GitHub {resp.status_code}: {resp.text[:80]}")
        return []

    files = []
    for item in resp.json():
        if item["type"] == "file":
            ext = os.path.splitext(item["name"])[1].lower()
            if ext in SUPPORTED:
                files.append({
                    "name": item["name"],
                    "path": item["path"],
                    "download_url": item["download_url"],
                    "repo": repo,
                    "size_kb": round(item.get("size", 0) / 1024, 1),
                })
        elif item["type"] == "dir":
            # Recursively get files in subfolders too
            files.extend(list_files_in_path(repo, item["path"]))
    return files


def download_selected_files(selected_files, output_dir, progress_callback=None):
    """Downloads only the files the user selected."""
    def log(msg):
        print(msg)
        if progress_callback:
            progress_callback(msg)

    os.makedirs(output_dir, exist_ok=True)
    downloaded = []

    for file_info in selected_files:
        name = file_info["name"]
        out_path = os.path.join(output_dir, name)

        if os.path.exists(out_path):
            log(f"  Already exists: {name}")
            downloaded.append(out_path)
            continue

        try:
            resp = requests.get(
                file_info["download_url"],
                headers=_headers(),
                timeout=30,
            )
            if resp.status_code == 200:
                with open(out_path, "wb") as f:
                    f.write(resp.content)
                log(f"  ✓ Downloaded: {name}")
                downloaded.append(out_path)
            else:
                log(f"  ✗ Failed: {name} ({resp.status_code})")
        except Exception as e:
            log(f"  ✗ Error: {name}: {e}")

    return downloaded


def fetch_all_from_github(output_dir, repo=None, progress_callback=None):
    """Legacy function — fetches everything from one repo. Kept for terminal mode."""
    def log(msg):
        print(msg)
        if progress_callback:
            progress_callback(msg)

    repo = repo or get_all_repos()[0] if get_all_repos() else ""
    if not repo:
        log("  No GitHub repo set. Skipping.")
        return []

    log(f"  Scanning: {repo}")
    files = list_files_in_path(repo)
    if not files:
        log("  No supported files found.")
        return []

    return download_selected_files(files, output_dir, progress_callback)