import requests
import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = os.getenv("GITHUB_REPO")


def get_headers():
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    return headers


def list_pdfs_in_repo(repo=None, path=""):
    repo = repo or REPO
    if not repo:
        print("  No GitHub repo specified. Skipping.")
        return []

    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    print(f"  Checking: {url}")

    response = requests.get(url, headers=get_headers())

    if response.status_code != 200:
        print(f"  GitHub error {response.status_code}: {response.text[:100]}")
        return []

    items = response.json()
    pdfs = []

    for item in items:
        if item["type"] == "file" and item["name"].endswith(".pdf"):
            pdfs.append({
                "name": item["name"],
                "download_url": item["download_url"],
                "path": item["path"]
            })
        elif item["type"] == "dir":
            pdfs.extend(list_pdfs_in_repo(repo, item["path"]))

    return pdfs


def download_pdf(pdf_info, output_dir):
    response = requests.get(
        pdf_info["download_url"],
        headers=get_headers()
    )

    if response.status_code == 200:
        filepath = os.path.join(output_dir, pdf_info["name"])
        with open(filepath, "wb") as f:
            f.write(response.content)
        print(f"  Downloaded: {pdf_info['name']}")
        return filepath
    else:
        print(f"  Failed to download: {pdf_info['name']}")
        return None


def fetch_all_from_github(output_dir, repo=None):
    print(f"\nFetching PDFs from GitHub...")
    pdfs = list_pdfs_in_repo(repo)

    if not pdfs:
        print("  No PDFs found in repo.")
        return []

    print(f"  Found {len(pdfs)} PDF(s)")
    downloaded = []

    for pdf in pdfs:
        path = download_pdf(pdf, output_dir)
        if path:
            downloaded.append(path)

    return downloaded