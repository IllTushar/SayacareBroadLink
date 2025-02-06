import requests as rq


class Email:
    @staticmethod
    def emailSendToAdmin(temperature, humidity):
        url = "https://samasya.tech/api/email-send"
        # emails = ['shivangi@sayacare.in', 'dmg@sayacare.in']
        emails = ['tushar@sayacare.in']
        for email in emails:
            data = {
                "to": f"{email}",
                "subject": "WareHouse temperature Alert!!",
                "text": f"WareHouse temperature goes sever!!\n Temperature= {temperature}°C ,Humidity = {humidity}%\n",
                "html": f"<p>WareHouse temperature goes severe!!<br>Temperature= {temperature}°C , Humidity = {humidity}%</p> \n <a href=\"https://samasya.net.in/#/Login_Page\">Go to Samasya Portal</a>"
            }

            try:
                resposne = rq.post(url, data=data)
                if resposne.status_code == 200:
                    print(f"Email send to {email}!!")
                else:
                    print("Something went wrong in node mailer api!!")
            except rq.RequestException as e:
                print(f"❌ Exception while sending request: {e}")
