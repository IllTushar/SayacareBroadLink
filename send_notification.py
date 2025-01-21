import requests as rq


class Notification:
    def __init__(self):
        pass

    @staticmethod
    def send_notification(temperature, message):
        url = "https://samasya.tech/api/group_push/main"
        temp = ""
        if temperature < 15:
            temp = f"Low Temperature {temperature}°C"
        elif 30 <= temperature <= 1000:
            temp = f"High Temperature {temperature}°C"

        data = {
            "message": {
                "notification": {
                    "title": "Temperature Alert!!",
                    "body": f"{temp}"
                },
                "topic": "7668270442"
            }
        }
        response = rq.post(url, json=data)

        if response.status_code == 200:
            print("Success: ", message)
        else:
            print("Error: ", response.status_code)
