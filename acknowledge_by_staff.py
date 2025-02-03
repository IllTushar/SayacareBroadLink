import requests as rq


class Acknowledgement:

    @staticmethod
    def acknowledgement_api():
        url = 'https://samasya.tech/api/warehouse/check-acknowledge-status'
        try:
            response = rq.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()  # Convert response to JSON

                if "status" in data:  # Check if 'status' key exists
                    if data['status'] is True:
                        print(f'{data['status']}')
                        return data['status'], data['phone_number'], data['acknowledge_status'], data['fixed_by_status']
                    else:
                        return data['status']
                else:
                    print("Status key not found in response.")
        except rq.exceptions.RequestException as e:
            print(f"Request failed: {e}")
