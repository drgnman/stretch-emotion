import csv
class FileOperator:
    def readCSVFile(self, filename):
        with open(filename, mode='r', newline='', encoding='utf-8') as file:
            # csv.readerを使用してファイルを読み込む。delimiter='\t' でタブ区切りを指定
            reader = csv.reader(file, delimiter='\t')
            next(reader)
            # ファイルの内容をリストに変換
            return list(reader)

    def readFile(self, filename):
        result = []
        with open(filename, "r") as file:
            for line in file:
                data = line.strip().split("\t")
                result.append(data)
            return result

    def writeFileSingleData(self, filepath, data):
        with open(filepath, "a") as file:
            file.write(",".join(data) + "\n")

    def writeFileAllData(self, filepath, datalist):
        with open(filepath, "w") as file:
            for data in datalist:
                file.write(",".join(data) + "\n")