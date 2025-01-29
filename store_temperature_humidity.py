import shelve
import requests
from datetime import datetime


class StoreTemperature:
    @staticmethod
    def update_temperature_on_server(temperature, humidity, mac_address, ware_house_name, current_date):
        url = "https://saya.net.in/api/warehouse-temperature"

        # Ensure mac_address is a string (convert bytearray to hex string if necessary)
        if isinstance(mac_address, bytearray):
            mac_address = mac_address.hex()

        with shelve.open("temp_database.db", flag='c', writeback=True) as prefs:
            timeStamp = prefs.get("timeStamp", None)
            current_time = datetime.now()

            # If database is empty (no timestamp), hit API
            if not timeStamp:
                send_data = True
            else:
                # Convert timestamp string to datetime
                previous_time = datetime.strptime(timeStamp, "%Y-%m-%d %H:%M:%S")
                time_diff = (current_time - previous_time).total_seconds() / 60  # Convert to minutes

                # Hit API only if the time difference is greater than 60 minutes
                send_data = time_diff > 60

            if send_data:
                # Prepare the data to send to the server
                data = {
                    "temperature": temperature,
                    "humidity": humidity,
                    "mac_address": mac_address,
                    "warehouse_name": ware_house_name,
                    "recorded_at": current_date,
                    "device_status": "active",
                    "data_quality": "good"
                }

                try:
                    response = requests.post(url, json=data)

                    if response.status_code == 200:
                        print(f"✅ Data sent successfully at {current_time}")
                        prefs["timeStamp"] = current_time.strftime("%Y-%m-%d %H:%M:%S")  # Update timestamp
                    else:
                        print(f"❌ Error {response.status_code}: {response.text}")

                except requests.RequestException as e:
                    print(f"❌ Exception: {e}")
            else:
                print("⏳ Skipping API call: Last timestamp is within 60 minute.")
