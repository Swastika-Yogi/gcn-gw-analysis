"""Download (if needed) and load the GCN circulars archive into memory."""
import io
import json
import os
import tarfile

import requests

ARCHIVE_URL = "https://gcn.nasa.gov/circulars/archive.json.tar.gz"
DEFAULT_OUTPUT_DIR = "./jsons"
DEFAULT_FOLDER = "./jsons/archive.json"


def download_and_extract(output_dir=DEFAULT_OUTPUT_DIR, force=False):
    """Download and extract the archive tarball. Skips download if the
    extracted folder already exists, unless force=True."""
    folder_path = os.path.join(output_dir, "archive.json")

    if os.path.exists(folder_path) and not force:
        print(f"Archive already present at {folder_path}, skipping download.")
        return folder_path

    os.makedirs(output_dir, exist_ok=True)

    print("Downloading and extracting...")
    response = requests.get(ARCHIVE_URL)
    if response.status_code != 200:
        raise RuntimeError(f"Failed to download archive. Status: {response.status_code}")

    with tarfile.open(fileobj=io.BytesIO(response.content), mode="r:gz") as tar:
        tar.extractall(path=output_dir)

    print(f"Success! Files extracted to {output_dir}")
    return folder_path


def load_circulars(folder_path=DEFAULT_FOLDER):
    """Load every circular JSON file in folder_path.

    Returns a list of (filename, data) tuples. Files that fail to parse
    are silently skipped (malformed archive entries).
    """
    files = os.listdir(folder_path)
    circulars = []

    for i, file in enumerate(files):
        if i % 5000 == 0:
            print(f"Loading circulars: {i}/{len(files)}")
        try:
            with open(os.path.join(folder_path, file), "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue
        circulars.append((file, data))

    return circulars


def circular_text(data):
    """Concatenated subject + body text for a circular record."""
    return str(data.get("subject", "")) + " " + str(data.get("body", ""))
