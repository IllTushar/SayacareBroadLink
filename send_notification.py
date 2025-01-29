import requests as rq

import os


class Notification:

    @staticmethod
    def send_notification(temperature, humidity, phone_numbers,file_path):
        url = "https://samasya.tech/api/group_push/main"

        # Ensure temperature is an integer or float
        if temperature is None or humidity is None:
            print("Error: Temperature or humidity is missing.")
            return

        # Define notification message based on temperature
        if temperature < 15 or humidity < 30:
            temp_message = f"Low Temperature {temperature}°C and humidity {humidity}%"
        elif 30 <= temperature <= 1000 or 60 <= humidity <= 100:
            temp_message = f"High Temperature {temperature}°C and humidity {humidity}%"
        else:
            print("Temperature is in the normal range. No notification sent.")
            return  # Exit if temperature is normal

        # Check if file exists before accessing it
        if not os.path.exists(file_path):
            print(f"Error: File {file_path} not found.")
            return

        if not phone_numbers:
            print("Error: No phone numbers found.")
            return

        # Send notification to each phone number
        for number in phone_numbers:
            data = {
                "message": {
                    "notification": {
                        "title": "Temperature Alert!!",
                        "body": temp_message
                    },
                    "topic": f"{number}"
                }
            }

            try:
                response = rq.post(url, json=data)

                if response.status_code == 200:
                    print(f"✅ Success: Notification sent to {number}!")
                else:
                    print(f"❌ Error {response.status_code}: {response.text}")

            except rq.RequestException as e:
                print(f"❌ Exception while sending request: {e}")
