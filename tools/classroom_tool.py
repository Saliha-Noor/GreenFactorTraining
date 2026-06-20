import os
import io
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

#SCOPES = [
 #   "https://www.googleapis.com/auth/classroom.courses.readonly",
  #  "https://www.googleapis.com/auth/classroom.coursework.materials.readonly",
   # "https://www.googleapis.com/auth/classroom.courseworkmaterials.readonly",
    #"https://www.googleapis.com/auth/classroom.announcements.readonly",
    #"https://www.googleapis.com/auth/drive.readonly",
#]
SCOPES = [
    "https://www.googleapis.com/auth/classroom.courses.readonly",
    "https://www.googleapis.com/auth/classroom.courseworkmaterials.readonly", # Note: This one is correct
    "https://www.googleapis.com/auth/classroom.announcements.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]

SUPPORTED = (".pdf", ".pptx", ".docx", ".txt", ".ppt")

GOOGLE_EXPORT = {
    "application/vnd.google-apps.presentation": (
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        ".pptx",
    ),
    "application/vnd.google-apps.document": (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".docx",
    ),
}


def get_credentials(token_path="token.json"):
    creds = None
    if os.path.exists(token_path):
        try:
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        except Exception:
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                creds = None
        if not creds:
            if not os.path.exists("credentials.json"):
                raise FileNotFoundError(
                    "credentials.json not found. Download from Google Cloud Console."
                )
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as f:
            f.write(creds.to_json())

    return creds


def list_enrolled_courses(token_path="token.json"):
    creds = get_credentials(token_path)
    service = build("classroom", "v1", credentials=creds)
    all_courses = []
    page_token = None
    while True:
        resp = service.courses().list(
            courseStates=["ACTIVE"], pageToken=page_token
        ).execute()
        all_courses.extend(resp.get("courses", []))
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    return [
        {
            "id": c["id"],
            "name": c["name"],
            "section": c.get("section", ""),
        }
        for c in all_courses
    ]
def list_materials_in_course(course_id, token_path="token.json"):
    """Returns all individual materials/lectures in a course for user to pick from."""
    creds = get_credentials(token_path)
    classroom = build("classroom", "v1", credentials=creds)
    drive = build("drive", "v3", credentials=creds)

    all_materials = []

    # Course work materials (lecture notes, slides)
    try:
        page_token = None
        while True:
            resp = classroom.courses().courseWorkMaterials().list(
                courseId=course_id, pageToken=page_token
            ).execute()
            for item in resp.get("courseWorkMaterial", []):
                for mat in item.get("materials", []):
                    if "driveFile" in mat:
                        df = mat["driveFile"]["driveFile"]
                        ext = os.path.splitext(df.get("title", ""))[1].lower()
                        if ext in SUPPORTED or _is_google_exportable(drive, df["id"]):
                            all_materials.append({
                                "id": df["id"],
                                "title": df.get("title", "Untitled"),
                                "type": "material",
                                "parent_title": item.get("title", ""),
                                "source": "classroom",
                            })
            page_token = resp.get("nextPageToken")
            if not page_token:
                break
    except Exception:
        pass

    # Coursework (assignments that have files)
    try:
        page_token = None
        while True:
            resp = classroom.courses().courseWork().list(
                courseId=course_id, pageToken=page_token
            ).execute()
            for item in resp.get("courseWork", []):
                for mat in item.get("materials", []):
                    if "driveFile" in mat:
                        df = mat["driveFile"]["driveFile"]
                        ext = os.path.splitext(df.get("title", ""))[1].lower()
                        if ext in SUPPORTED or _is_google_exportable(drive, df["id"]):
                            all_materials.append({
                                "id": df["id"],
                                "title": df.get("title", "Untitled"),
                                "type": "coursework",
                                "parent_title": item.get("title", ""),
                                "source": "classroom",
                            })
            page_token = resp.get("nextPageToken")
            if not page_token:
                break
    except Exception:
        pass

    # Announcements
    try:
        page_token = None
        while True:
            resp = classroom.courses().announcements().list(
                courseId=course_id, pageToken=page_token
            ).execute()
            for item in resp.get("announcements", []):
                for mat in item.get("materials", []):
                    if "driveFile" in mat:
                        df = mat["driveFile"]["driveFile"]
                        ext = os.path.splitext(df.get("title", ""))[1].lower()
                        if ext in SUPPORTED or _is_google_exportable(drive, df["id"]):
                            all_materials.append({
                                "id": df["id"],
                                "title": df.get("title", "Untitled"),
                                "type": "announcement",
                                "parent_title": item.get("text", "")[:50],
                                "source": "classroom",
                            })
            page_token = resp.get("nextPageToken")
            if not page_token:
                break
    except Exception:
        pass

    return all_materials


def _is_google_exportable(drive, file_id):
    """Check if file is a Google Doc/Slide that can be exported."""
    try:
        meta = drive.files().get(fileId=file_id, fields="mimeType").execute()
        return meta.get("mimeType", "") in GOOGLE_EXPORT
    except Exception:
        return False


def download_selected_materials(
    selected_materials, output_dir,
    token_path="token.json", progress_callback=None
):
    """Downloads only the specific materials the user selected."""
    def log(msg):
        print(msg)
        if progress_callback:
            progress_callback(msg)

    creds = get_credentials(token_path)
    drive = build("drive", "v3", credentials=creds)
    os.makedirs(output_dir, exist_ok=True)
    downloaded = []

    for mat in selected_materials:
        path = _download_drive_file(
            drive, mat["id"], mat["title"], output_dir, log
        )
        if path:
            downloaded.append(path)

    log(f"  ✓ {len(downloaded)} file(s) downloaded")
    return downloaded

def fetch_materials_from_course(
    course_id, course_name, output_dir, token_path="token.json", progress_callback=None
):
    def log(msg):
        print(msg)
        if progress_callback:
            progress_callback(msg)

    creds = get_credentials(token_path)
    classroom = build("classroom", "v1", credentials=creds)
    drive = build("drive", "v3", credentials=creds)
    os.makedirs(output_dir, exist_ok=True)

    items = []
    seen_ids = set()

    for fetch_fn, key in [
        (lambda: classroom.courses().courseWorkMaterials().list(courseId=course_id).execute(), "courseWorkMaterial"),
        (lambda: classroom.courses().courseWork().list(courseId=course_id).execute(), "courseWork"),
        (lambda: classroom.courses().announcements().list(courseId=course_id).execute(), "announcements"),
    ]:
        try:
            items.extend(fetch_fn().get(key, []))
        except Exception as e:
            log(f"  Note: {e}")

    log(f"  Found {len(items)} item(s) in {course_name}")
    downloaded = []

    for item in items:
        for mat in item.get("materials", []):
            if "driveFile" not in mat:
                continue
            df = mat["driveFile"]["driveFile"]
            file_id = df["id"]
            title = df.get("title", "file")
            if file_id in seen_ids:
                continue
            seen_ids.add(file_id)
            path = _download_drive_file(drive, file_id, title, output_dir, log)
            if path:
                downloaded.append(path)

    log(f"  ✓ {len(downloaded)} file(s) downloaded")
    return downloaded


def _download_drive_file(drive, file_id, title, output_dir, log):
    safe = "".join(c for c in title if c.isalnum() or c in "._- ").strip()
    try:
        meta = drive.files().get(fileId=file_id, fields="mimeType").execute()
        mime = meta.get("mimeType", "")
    except Exception as e:
        log(f"  ✗ Metadata error for {safe}: {e}")
        return None

    if mime in GOOGLE_EXPORT:
        export_mime, ext = GOOGLE_EXPORT[mime]
        out_path = os.path.join(output_dir, safe + ext)
        if os.path.exists(out_path):
            return out_path
        request = drive.files().export_media(fileId=file_id, mimeType=export_mime)
    elif "application/vnd.google-apps" in mime:
        log(f"  Skipping Google type: {safe}")
        return None
    else:
        ext = os.path.splitext(safe)[1].lower()
        if ext not in SUPPORTED:
            return None
        out_path = os.path.join(output_dir, safe)
        if os.path.exists(out_path):
            return out_path
        request = drive.files().get_media(fileId=file_id)

    try:
        fh = io.BytesIO()
        dl = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            _, done = dl.next_chunk()
        with open(out_path, "wb") as f:
            f.write(fh.getvalue())
        log(f"  ✓ Downloaded: {os.path.basename(out_path)}")
        return out_path
    except Exception as e:
        log(f"  ✗ Download failed {safe}: {e}")
        return None