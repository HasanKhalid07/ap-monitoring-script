#  AP Monitoring Script

A lightweight Python-based Access Point (AP) monitoring tool designed to detect down or missing APs by comparing live WLC output with a predefined inventory list.

---

##  Overview

This script connects to a Wireless LAN Controller (WLC) via SSH, retrieves live AP status information, and compares it against a master AP list to identify missing or down APs.

It is designed to be simple, efficient, and independent of enterprise monitoring platforms.

---

##  Key Features

- SSH-based WLC access
- Parses show ap summary CLI output
- Extracts only registered (joined) APs
- Compares live data with inventory list
- Identifies missing/down APs
- Clean parsing logic with error handling

---

##  Technologies Used

- Python 3
- Paramiko (SSH)
- CLI Output Parsing
- Set Comparison Logic

---

##  How It Works

1. Connects to WLC via SSH  
2. Runs show ap summary  
3. Extracts AP names in Registered state  
4. Compares with master inventory  
5. Displays missing APs as DOWN  

---

##  How to Run

### Install Requirements

pip install -r requirements.txt

### Run Script

python main.py

---

##  Security Note

All credentials and sensitive information are removed.

---

##  Future Improvements

- Email alerts
- Telegram/Slack integration
- Scheduled automation
- Logging system
- REST API integration

---

##  What This Project Demonstrates

- Network automation skills
- Python for networking
- CLI parsing logic
- Monitoring workflow design

---

 Feel free to fork and improve.
