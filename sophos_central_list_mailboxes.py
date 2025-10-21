#Created by jmsoares91 @ 21/10/2025 @ version 1.0
#!/usr/bin/env python3
import requests
from tabulate import tabulate
import csv
from datetime import datetime
import os
from tqdm import tqdm

# ==== CONFIGURATION ====
# To configure the bellow, check the follwing tutorial: https://www.youtube.com/watch?v=O1Yg71OtDJA
JWT = ""
TENANT_ID = ""
DATA_REGION = "https://api-XXXX.central.sophos.com"  # change to the correct region
PAGESIZE = 50  # maximum allowed by Sophos API

def list_all_mailboxes():
    headers = {
        "Authorization": f"Bearer {JWT}",
        "X-Tenant-ID": TENANT_ID
    }

    page_from_key = 0
    all_mailboxes = []
    headers_table = ["ID", "Type", "Email", "Name", "Created At", "Bulk Sender Privilege", "Blocked", "Aliases"]

    # Create CSV on the same directory where the script is executed
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(current_dir, f"mailboxes_{timestamp}.csv")

    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers_table)
        writer.writeheader()

        total_processed = 0

        # Loop with progress bar
        pbar = tqdm(total=15000, desc="Processing Mailboxes", unit="mb")  # total should be more than the maximum number of mailboxes that Central has

        while True:
            url = f"{DATA_REGION}/email/v1/mailboxes?pagesize={PAGESIZE}&pageFromKey={page_from_key}"
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                print(f"\n❌ Error {response.status_code}: {response.text}")
                break

            data = response.json()
            items = data.get("items", [])
            if not items:
                break  # page end

            for mb in items:
                writer.writerow({
                    "ID": mb.get("id"),
                    "Type": mb.get("type"),
                    "Email": mb.get("email"),
                    "Name": mb.get("name"),
                    "Created At": mb.get("createdAt"),
                    "Bulk Sender Privilege": mb.get("bulkSenderPrivilege"),
                    "Blocked": mb.get("blocked"),
                    "Aliases": ",".join(mb.get("aliases", []))
                })

            total_processed += len(items)
            pbar.update(len(items))  # updates status bar

            # Next page
            pages = data.get("pages", {})
            next_key = pages.get("nextKey")
            if next_key is not None:
                page_from_key = int(next_key)
            else:
                break

        pbar.close()

    print(f"\n📁 Results exported to: {filename}")
    print(f"✅ Total exported mailboxes: {total_processed}")

# ==== EXECUTAR ====
if __name__ == "__main__":
    list_all_mailboxes()