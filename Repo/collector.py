import paramiko
import time
import json
import os
import re
from datetime import datetime

# ================= CONFIG =================
WLC_IP = ""
USERNAME = ""
PASSWORD = ""

JSON_FILE = "ap_status.json"
# ==========================================


# ================= SSH =================
def ssh_command(command):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh.connect(
        WLC_IP,
        username=USERNAME,
        password=PASSWORD,
        look_for_keys=False,
        allow_agent=False
    )

    shell = ssh.invoke_shell()
    time.sleep(1)

    shell.send("terminal length 0\n")
    time.sleep(1)

    shell.send(command + "\n")
    time.sleep(3)

    # Get all output
    output = ""
    while True:
        if shell.recv_ready():
            output += shell.recv(999999).decode(errors="ignore")
        else:
            time.sleep(0.5)
            # Try one more time
            if shell.recv_ready():
                output += shell.recv(999999).decode(errors="ignore")
            else:
                break

    ssh.close()
    return output


# ================= PARSE AP SUMMARY =================
def get_wlc_ap_summary():
    output = ssh_command("show ap summary")
    
    aps = {}
    parse = False
    
    for line in output.splitlines():
        if line.startswith("AP Name"):
            parse = True
            continue
        
        if not parse or line.strip() == "" or line.startswith("---"):
            continue
        
        parts = line.split()
        
        # Expected format: AP Name Slots AP Model Ethernet MAC Radio MAC Location etc.
        if len(parts) < 4:
            continue
        
        ap_name = parts[0]
        
        # Skip lines with *
        if ap_name.startswith("*"):
            continue
        
        ap_model = parts[2]
        ap_mac = parts[3]
        
        aps[ap_name] = {
            "mac": ap_mac,
            "model": ap_model
        }
    
    return aps


# ================= PARSE CDP (USING REGEX FROM FIRST SCRIPT) =================
def get_wlc_cdp():
    output = ssh_command("show ap cdp neighbors")
    
    cdp = {}
    
    # Use the same regex pattern from your first script
    pattern = r"(\S+)\s+(\d+\.\d+\.\d+\.\d+)\s+(\S+)\s+(\d+\.\d+\.\d+\.\d+)\s+(\S+)"
    
    for line in output.splitlines():
        match = re.match(pattern, line)
        if match:
            ap_name = match.group(1)
            ap_ip = match.group(2)
            switch_name = match.group(3)
            switch_ip = match.group(4)
            switch_port = match.group(5)
            
            cdp[ap_name] = {
                "ap_ip": ap_ip,
                "switch": switch_name,
                "ip": switch_ip,
                "port": switch_port
            }
    
    return cdp


# ================= LOAD EXISTING JSON =================
def load_json():
    if not os.path.exists(JSON_FILE):
        return []
    
    with open(JSON_FILE, "r") as f:
        return json.load(f)


# ================= SAVE JSON =================
def save_json(data):
    with open(JSON_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ================= MAIN =================
def main():
    print("\n[INFO] Collecting WLC AP Data")
    
    # Get AP summary
    print("[INFO] Getting AP summary...")
    ap_summary = get_wlc_ap_summary()
    print(f"[INFO] Found {len(ap_summary)} APs in summary")
    
    # Get CDP neighbors
    print("[INFO] Getting CDP neighbors...")
    ap_cdp = get_wlc_cdp()
    print(f"[INFO] Found {len(ap_cdp)} APs with CDP info")
    
    # Load existing JSON data
    json_data = load_json()
    json_map = {ap["AP Name"]: ap for ap in json_data}
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    live_ap_set = set(ap_summary.keys())
    
    print(f"\n[INFO] Processing {len(live_ap_set)} live APs")
    
    # ===== PROCESS LIVE APS =====
    for ap_name, ap_data in ap_summary.items():
        mac = ap_data["mac"]
        model = ap_data["model"]
        
        # Get CDP info if available
        switch = ""
        port = ""
        switch_ip = ""
        ap_ip = ""
        
        if ap_name in ap_cdp:
            cdp_info = ap_cdp[ap_name]
            switch = cdp_info.get("switch", "")
            port = cdp_info.get("port", "")
            switch_ip = cdp_info.get("ip", "")
            ap_ip = cdp_info.get("ap_ip", "")
        
        # ---------- NEW AP ----------
        if ap_name not in json_map:
            print(f"[NEW AP] {ap_name}")
            
            json_data.append({
                "AP Name": ap_name,
                "AP IP": ap_ip,
                "AP MAC": mac,
                "AP Model": model,
                "Switch Name": switch,
                "Switch IP": switch_ip,
                "Switch Port": port,
                "Status": "UP",
                "Last Seen": now
            })
            continue
        
        # ---------- EXISTING AP ----------
        entry = json_map[ap_name]
        
        entry["AP MAC"] = mac
        entry["AP Model"] = model
        entry["Switch Name"] = switch
        entry["Switch IP"] = switch_ip
        entry["Switch Port"] = port
        entry["AP IP"] = ap_ip
        entry["Status"] = "UP"
        entry["Last Seen"] = now
    
    # ===== MARK DOWN APs =====
    down_count = 0
    for entry in json_data:
        if entry["AP Name"] not in live_ap_set:
            if entry["Status"] != "DOWN":
                print(f"[DOWN] {entry['AP Name']}")
                down_count += 1
            entry["Status"] = "DOWN"
    
    # Save updated data
    save_json(json_data)
    
    print(f"\n[OK] JSON Updated Successfully")
    print(f"[STATS] Total APs in JSON: {len(json_data)}")
    print(f"[STATS] UP APs: {len(live_ap_set)}")
    print(f"[STATS] DOWN APs: {down_count}")
    print(f"[STATS] Unknown APs (in JSON but not live): {len(json_data) - len(live_ap_set) - down_count}\n")


# ================= RUN =================
if __name__ == "__main__":
    main()