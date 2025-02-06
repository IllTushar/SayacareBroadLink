import broadlink as bl
from datetime import datetime, timedelta
import schedule
import time
import shelve
from send_notification import Notification
import atexit
import signal
import sys
from store_temperature_humidity import StoreTemperature
from acknowledge_by_staff import Acknowledgement
from Staff_Info import Staff_Info
from send_email import Email

'''
When you connect broadlink device then disable the lock info from the broadlink app
otherwise auth issue occurs 
'''


def clear_shelve():
    """Clears the shared_prefs.db shelve database."""
    with shelve.open("shared_prefs.db") as prefs:
        prefs.clear()
    print("Shared preferences cleared.")


def clear_shelve_for_fixed_timestamp():
    with shelve.open("timeStampForFixed") as prefs:
        prefs.clear()
    print("Reset timeStampForFixed!!")


def fetch_data_from_broadlink_devices():
    devices = bl.discover(timeout=5)

    if not devices:
        print("No Broadlink devices found.")
        Notification.send_notification_to_dev()
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

                # Schedule the function to run every 1 hour
                StoreTemperature.update_temperature_on_server(
                    temperature=temperature, humidity=humidity,
                    mac_address=mac,
                    ware_house_name="Main Warehouse",
                    current_date=current_date)

                temperature_validation(temperature, humidity)

            except AttributeError:
                print("This device does not support sensor data.")
            except Exception as e:
                print(f"Error while fetching sensor data: {e}")
        except Exception as e:
            print(f"Error initializing device: {e}")


def temperature_validation(temperature, humidity):
    with shelve.open("shared_prefs.db", flag='c', writeback=True) as prefs:  # Use 'c' mode (create if needed)
        timeStamp = prefs.get("timeStamp", None)
        current_time = datetime.now()

        # Parse timeStamp if it exists
        if timeStamp:
            timeStamp = datetime.strptime(timeStamp, "%Y-%m-%d %H:%M:%S")

        # Check if temperature is within the normal range
        if 15 <= temperature <= 25 and 30 <= humidity <= 60:
            print(
                f"Temperature = {temperature}°C and Humidity = {humidity}% is within the normal range. No action required.")
            return

        # File path where staff numbers are stored
        file_path = r'C:\Users\gtush\Desktop\split_files\operations.csv'
        # Fetch phone numbers
        phone_numbers = Staff_Info.getStaff_Phone_Number(file_path)

        # Check for user acknowledgment
        acknowledger_status, fixed_by, acknowledger_phone_number = Acknowledgement.acknowledgement_api()
        with shelve.open("fixed_by_time.db", flag='c', writeback=True) as fixed_prefs:
            if acknowledger_status and fixed_by:
                timeStampForFixed = prefs.get("timeStampForFixed", None)
                if timeStampForFixed is None:
                    fixed_prefs["status"] = True
                    fixed_prefs.sync()
                    if acknowledger_phone_number is not None:
                        Notification.send_notification_to_acknowledge(phone_numbers,
                                                                      acknowledger_phone_number, fixed_by)
                        print(f"send notification to all that issue fixed by {acknowledger_phone_number}")
                    return
                else:
                    return
            else:
                clear_shelve_for_fixed_timestamp()
                if acknowledger_status:
                    Notification.send_notification_to_acknowledge(phone_numbers,
                                                                  acknowledger_phone_number, fixed_by)
                    print(f"send notification to all that issue acknowledged by {acknowledger_phone_number}")
                    return

        # Check if enough time has passed to send another notification
        if not timeStamp or (current_time - timeStamp) >= timedelta(minutes=30):

            if temperature < 40 or humidity < 65:
                Notification.send_notification(temperature, humidity, phone_numbers, file_path)
            else:  # temperature >= 40
                Notification.send_notification(temperature, humidity, phone_numbers, file_path)
                Email.emailSendToAdmin(temperature, humidity)  # Send email to admin
                print("Email sent to admin!")

            # Store the current timestamp after sending the notification
            prefs["timeStamp"] = current_time.strftime("%Y-%m-%d %H:%M:%S")
            prefs.sync()  # Ensure data is written to disk
            print("TimeStamp stored in shared preferences.")
        else:
            print("No need to send acknowledgment (within 30 minutes).")

        # Reset timeStamp if more than 30 minutes have passed
        if timeStamp and (current_time - timeStamp) > timedelta(minutes=30):
            prefs["timeStamp"] = None
            prefs.sync()  # Ensure data is written to disk
            print("TimeStamp reset to None.")


# Exit safely
def handle_exit(signum=None, frame=None):
    """Handles forced termination signals and clears shelve."""
    print("Program is stopping. Cleaning up shared preferences...")
    clear_shelve()
    sys.exit(0)


# Register cleanup functions
atexit.register(clear_shelve)  # Runs on normal exit
signal.signal(signal.SIGINT, handle_exit)  # Handle Ctrl+C
signal.signal(signal.SIGTERM, handle_exit)

if __name__ == "__main__":
    # Schedule the task to run every 5 minutes
    schedule.every(1).minutes.do(fetch_data_from_broadlink_devices)

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        handle_exit()
