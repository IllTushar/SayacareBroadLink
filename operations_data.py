import pandas as pd
from dataclasses import dataclass
from typing import List


@dataclass
class Model:
    id: int
    phone_number: str
    name: str

    def to_dict(self):
        return {
            "id": self.id,
            "phone_number": self.phone_number,
            "name": self.name
        }


def data_cleaning(read_file):
    dataList: List[Model] = []
    count = 0
    for _, row in read_file.iterrows():
        if row['role'] == "packer" or row['role'] == "assembler" and row['name'] != "Sahil":
            count = count + 1
            model = Model(count, row['phone_number'], row['name'])
            dataList.append(model)
    df = pd.DataFrame([item.to_dict() for item in dataList])
    df.to_csv(r"C:\Users\gtush\Desktop\split_files\operations.csv", index=False)


if __name__ == '__main__':
    file_path = r'C:\Users\gtush\Desktop\split_files\Staff Table - Sheet1.csv'
    read_file = pd.read_csv(file_path)
    data_cleaning(read_file)
