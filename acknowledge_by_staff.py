import requests as rq


class Acknowledgement:

    @staticmethod
    def acknowledgement_api():
        url = 'https://saya.net.in/api/warehouse/check-acknowledge-status'
        try:
            response = rq.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()  # Convert response to JSON

                if "status" in data:  # Check if 'status' key exists
                    print(f'{data['status']}')
                    return data['status'], data['status'], data['status']
                else:
                    print("Status key not found in response.")
        except rq.exceptions.RequestException as e:
            print(f"Request failed: {e}")
