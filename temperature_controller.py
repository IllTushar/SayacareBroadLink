import broadlink as bl
from datetime import datetime, timedelta
import schedule
import time
import shelve
from send_notification import Notification

'''
When you connect broadlink device then disable the lock info from the broadlink app
otherwise auth issue occurs 
'''


def fetch_data_from_broadlink_devices():
    devices = bl.discover(timeout=5)

    if not devices:
        print("No Broadlink devices found.")
        exit()

    # Print discovered devices and store their information
    for item in devices:
        print(f"Discovered device: {item}")
        print("Device Details:")
        print(f"  Host: {item.host[0]}")  # Correctly access the IP address from the tuple
        print(f"  MAC Address: {item.mac.hex()}")  # MAC address in hexadecimal
        print(f"  Device Type: {hex(item.devtype)}")  # This prints the device type as a hex string

    for item in devices:
        host = item.host  # Device IP address (host already contains the tuple)
        mac = bytearray.fromhex(item.mac.hex())  # Device MAC address (hex)
        device_type = item.devtype  # Device type should be an integer (no need to convert to hex)

        # Ensure host is passed as a tuple (IP address, port)
        if isinstance(host, tuple):
            host = host[0], host[1]  # Extract tuple elements if needed (IP address and port)
        else:
            host = (host, 80)  # Default port 80 if host is not a tuple

        try:
            # Initialize the device using the device's type, host, and MAC address
            device = bl.gendevice(device_type, host, mac)

            # Authenticate with the device (without passing a password)
            if device.auth():  # No argument needed
                print("Authentication successful.")
            else:
                print("Authentication failed. This may indicate an incorrect password or a setup issue.")
                exit()

            # Fetch temperature and humidity data (if supported)
            try:
                data = device.check_sensors()  # Ensure your device supports this function
                temperature = data.get("temperature", "N/A")
                humidity = data.get("humidity", "N/A")
                current_date = datetime.now().strftime("%d-%b-%Y %I:%M:%S %p")
                print(f"Temperature: {temperature}°C")
                print(f"Humidity: {humidity}%")
                print(f'current_date: {current_date}')
                temperature_validation(30)
            except AttributeError:
                print("This device does not support sensor data.")
            except Exception as e:
                print(f"Error while fetching sensor data: {e}")

        except Exception as e:
            print(f"Error initializing device: {e}")


def temperature_validation(temperature):
    with shelve.open("shared_prefs.db") as prefs:
        timeStamp = prefs.get("timeStamp", None)
        current_time = datetime.now()

        # Parse timeStamp if it exists
        if timeStamp:
            timeStamp = datetime.strptime(timeStamp, "%Y-%m-%d %H:%M:%S")

        # Check if temperature is within the normal range
        if 15 <= temperature <= 25:
            print("Temperature is within the normal range. No action required.")
            return

        # Check for user acknowledgment
        apiStatus = getUserAcknowledgment()
        if apiStatus:
            print("User acknowledgment received. No further action needed.")
            return

        # Helper function to send notifications or emails

        # Check if enough time has passed to send another notification
        if not timeStamp or (current_time - timeStamp) >= timedelta(minutes=2):
            if temperature < 40:
                Notification.send_notification(temperature)
            else:  # temperature >= 40
                Notification.send_notification(temperature)
                emailSendToAdmin(temperature)  # Send email to admin
                print("Email sent to admin!")

            # Store the current timestamp after sending the notification
            prefs["timeStamp"] = current_time.strftime("%Y-%m-%d %H:%M:%S")
            print("TimeStamp stored in shared preferences.")
        else:
            print("No need to send acknowledgment (within 2 minutes).")

        # Reset timeStamp if not already reset and time has passed
        if timeStamp and (current_time - timeStamp) > timedelta(minutes=2):
            prefs["timeStamp"] = None
            print("TimeStamp reset to None.")


def emailSendToAdmin(temperature):
    pass


def getUserAcknowledgment():
    pass


if __name__ == "__main__":
    # Schedule the task to run every 5 minutes
    schedule.every(1).minutes.do(fetch_data_from_broadlink_devices)

    while True:
        schedule.run_pending()
        time.sleep(1)
