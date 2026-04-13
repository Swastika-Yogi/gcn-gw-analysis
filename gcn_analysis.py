import os
import json
import re
import csv
import requests
import tarfile
import io
# =========================================
# STEP 1: Setup and download
# =========================================
url = "https://gcn.nasa.gov/circulars/archive.json.tar.gz"
output_dir = "./jsons"
folder_path = r"./jsons/archive.json"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

print("Downloading and extracting...")
response = requests.get(url)

if response.status_code == 200:
    # Open the tarball from memory
    with tarfile.open(fileobj=io.BytesIO(response.content), mode="r:gz") as tar:
        # Extract into the specific subfolder
        tar.extractall(path=output_dir)
        print(f"Success! Files extracted to {output_dir}")
else:
    print(f"Failed to download. Status: {response.status_code}")

files = os.listdir(folder_path)

print("Total files found:", len(files))


# =========================================
# STEP 2: Filter GW circulars + LOAD ONCE
# =========================================
gw_data = []   # (file, data)

for i, file in enumerate(files):

    # 🔥 progress indicator
    if i % 1000 == 0:
        print(f"Scanning files: {i}/{len(files)}")

    try:
        with open(os.path.join(folder_path, file), "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        continue

    text = (str(data.get("subject", "")) + " " + str(data.get("body", ""))).lower()

    if any(k in text for k in ["ligo", "virgo", "kagra"]):
        gw_data.append((file, data))

print("GW circulars:", len(gw_data))


# =========================================
# STEP 3: Extract event IDs
# =========================================
event_ids = []

for i, (file, data) in enumerate(gw_data):

    if i % 500 == 0:
        print(f"Extracting events: {i}/{len(gw_data)}")

    text = str(data.get("subject", "")) + " " + str(data.get("body", ""))

    matches = re.findall(r"S\d{6}[a-z]\b", text)
    event_ids.extend(matches)

unique_events = list(set(event_ids))
print("Unique events:", len(unique_events))


# =========================================
# STEP 4: Filter O4a events
# =========================================
o4a_events = []

for ev in unique_events:
    try:
        num = int(ev[1:7])
        if 230524 <= num <= 240116:
            o4a_events.append(ev)
    except:
        continue

print("O4a events:", len(o4a_events))


# =========================================
# STEP 5: Map event → circulars
# =========================================
event_to_circulars = {}

for file, data in gw_data:

    text = str(data.get("subject", "")) + " " + str(data.get("body", ""))

    matches = re.findall(r"S\d{6}[a-z]\b", text)

    for m in matches:
        if m in o4a_events:
            event_to_circulars.setdefault(m, []).append(file)

print("Total O4a events mapped:", len(event_to_circulars))


# =========================================
# STEP 6: Extract parameters
# =========================================
event_parameters = {}

for event, files_list in event_to_circulars.items():

    masses, distances, fars = [], [], []

    for file, data in gw_data:

        if file not in files_list:
            continue

        text = (str(data.get("subject", "")) + " " + str(data.get("body", ""))).lower()

        # MASS
        for m in re.findall(r"(mass|mchirp)[^0-9]{0,40}([0-9]+\.?[0-9]*)", text):
            try:
                val = float(m[1])
                if 1 < val < 200:
                    masses.append(val)
            except:
                continue

        # DISTANCE
        for d in re.findall(r"(distance|luminosity distance)[^0-9]{0,40}([0-9]+\.?[0-9]*)", text):
            try:
                val = float(d[1])
                if 1 < val < 10000:
                    distances.append(val)
            except:
                continue

        # FAR
        for f in re.findall(r"(far|false alarm rate)[^0-9]{0,40}([0-9\.e\-\+]+)", text):
            try:
                val = float(f[1])
                if val < 1e-2:
                    fars.append(val)
            except:
                continue

    event_parameters[event] = {
        "mass": masses,
        "distance": distances,
        "far": fars
    }


# =========================================
# STEP 7: Find best event
# =========================================
def score(e):
    p = event_parameters[e]
    return len(p["mass"]) + len(p["distance"]) + len(p["far"])

valid_events = [e for e in event_parameters if score(e) > 0]

if not valid_events:
    print("No usable events.")
    exit()

best_event = max(valid_events, key=score)

masses = event_parameters[best_event]["mass"]
distances = event_parameters[best_event]["distance"]
fars = event_parameters[best_event]["far"]

print("\nBest event:", best_event)
print("Circulars:", len(event_to_circulars[best_event]))


# =========================================
# STEP 8: CLEAN SUMMARY
# =========================================
print("\n--- CLEAN SUMMARY ---")
print("Avg mass:", sum(masses)/len(masses) if masses else None)
print("Avg distance:", sum(distances)/len(distances) if distances else None)
print("Best FAR:", min(fars) if fars else None)


# =========================================
# STEP 9: EXPORT CSV
# =========================================
output_file = r".\o4a_gw_dataset.csv"
rows = []

for event in event_parameters:

    masses = event_parameters[event]["mass"]
    distances = event_parameters[event]["distance"]
    fars = event_parameters[event]["far"]

    # keep only events with BOTH mass and distance (more useful scientifically)
    if not (masses and distances):
        continue

    row = {
        "event": event,
        "n_circulars": len(event_to_circulars.get(event, [])),
        "avg_mass": round(sum(masses)/len(masses), 3) if masses else "",
        "avg_distance": round(sum(distances)/len(distances), 3) if distances else "",
        "best_far": min(fars) if fars else "",
        "n_mass_points": len(masses),
        "n_distance_points": len(distances),
        "n_far_points": len(fars)
    }

    rows.append(row)

with open(output_file, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=row.keys())
    writer.writeheader()
    writer.writerows(rows)

print("\nCSV dataset saved at:", output_file)
print("Total usable events:", len(rows))
