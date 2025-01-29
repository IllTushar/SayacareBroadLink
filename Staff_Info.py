import pandas as pd
from typing import List


class Staff_Info:
    @staticmethod
    def getStaff_Phone_Number(file_path):
        numbers: List[str] = []
        read_file = pd.read_csv(file_path)
        for index, row in read_file.iterrows():
            numbers.append(row['phone_number'])
        return numbers
