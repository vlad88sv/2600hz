import requests
import csv

# Replace with your API details
API_ENDPOINT = "https://ui.zswitch.net/v2"  # e.g., 
AUTH_TOKEN = "ey..."
ROOT_ACCOUNT_ID = "..."

HEADERS = {
    "Content-Type": "application/json",
    "X-Auth-Token": AUTH_TOKEN
}


def get_descendant_accounts(account_id):
    """
    Fetch all descendant accounts for a given account ID.
    """
    descendants = []
    url = f"{API_ENDPOINT}/accounts/{account_id}/descendants"
    params = {"paginate": "false"}

    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code == 200:
        descendants = response.json().get("data", [])
        print(f"Found {len(descendants)} descendant accounts.")
    else:
        print(f"Failed to fetch descendants: {response.status_code}, {response.text}")

    return descendants


def get_devices(account_id):
    """
    Fetch all devices for a given account ID.
    """
    devices = []
    url = f"{API_ENDPOINT}/accounts/{account_id}/devices"
    params = {
        "paginate": "false",
        "with_status": "true"
    }

    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code == 200:
        devices = response.json().get("data", [])
        print(f"  Found {len(devices)} devices for account {account_id}.")
    else:
        print(f"  Failed to fetch devices: {response.status_code}, {response.text}")

    return devices


def reboot_device(account_id, device_id):
    """
    Reboot a given device.
    """
    url = f"{API_ENDPOINT}/accounts/{account_id}/devices/{device_id}/sync"
    response = requests.post(url, headers=HEADERS)

    if response.status_code == 202:
        print(f"     Device {device_id} rebooted successfully.")
    else:
        print(f"     Failed to reboot device {device_id}: {response.status_code}, {response.text}")


def main():
    print("Starting device reboot process...")
    # Step 1: Fetch descendant accounts
    descendant_accounts = get_descendant_accounts(ROOT_ACCOUNT_ID)

    # Include root account itself
    all_accounts = [{"id": ROOT_ACCOUNT_ID}] + descendant_accounts

    i = 0


    with open("report.csv", "a", newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["Account ID", "MAC", "Device type", "Device ID", "Device name"])
        
        for account in all_accounts:
            i += 1
            account_id = account["id"]
            print(f"\nProcessing account #{i}: {account_id}")

            # Step 2: Fetch devices for the account
            devices = get_devices(account_id)

            # Step 3: Check if devices are registered and reboot if they are)
            for device in devices:
                device_id = device["id"]
                device_type = device["device_type"]
                device_name = device["name"]
                registered = device.get("registered", False)
                mac = device.get("mac", "000000000000")
                if registered:
                    #print(device)
                    print(f"    Device {mac} - {device_type} - {device_name} is registered. Rebooting...")
                    reboot_device(account_id, device_id)
                    writer.writerow([account_id, mac, device["device_type"], device_id, device["name"]])
                #else:
                #    print(f"Device {device_id} is not registered. Skipping.")

        print("\nDevice reboot process completed.")


if __name__ == "__main__":
    main()
