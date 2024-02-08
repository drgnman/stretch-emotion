import argparse
import copy
from Core import Core
from FileOperator import FileOperator
from Wordfeatures import Wordfeatures

# core = Core()
# parser = argparse.ArgumentParser()
# parser.add_argument("input_emotion", help="input file name")
# 
# args = parser.parse_args()
# 
# hoge, fuga = core.emotionTransferW2V(args.input_emotion)

core = Core()
parser = argparse.ArgumentParser()
parser.add_argument("input_filename", help="input file name")
parser.add_argument("output_filepath", help="output file path")

args = parser.parse_args()

# ファイル操作用、感情変換用のクラスオブジェクトを生成
fo = FileOperator()
wf = Wordfeatures()

# ファイルの読み込みと、出力リスト用のハードコピー
datalist = fo.readCSVFile(args.input_filename)
for i in range(len(datalist)):
    datalist[i] = [item for item in datalist[i] if item != '']
    # print(datalist[i])
datalist = [[int(row[0])]+row[1:] for row in datalist]
datalist.sort(key=lambda x:x[0])
output_datalist = copy.copy(datalist)

# 感情変換
for i in range(len(datalist)):
    output_datalist[i].insert(2, "")
    output_datalist[i][1], output_datalist[i][2] = core.stretchEmotion(datalist, datalist[i][1])
    # print("発話ID: ", output_datalist[i][0],"調整後の感情ID: ", output_datalist[i][1], "調整後の感情名: ", output_datalist[i][2])

# output_datalist = copy.copy(datalist)
output_datalist2 = []

for i in range(len(output_datalist)):
    if(wf.judgeSpecificWords(output_datalist[i][3]) != ""):
        output_datalist2.append(output_datalist[i])

output_datalist = [[str(row[0])]+row[1:] for row in output_datalist]
# output_datalist2 = [[str(row[0])]+row[1:] for row in output_datalist2]

# 結果書き出し
fo.writeFileAllData(args.output_filepath, output_datalist)
# fo.writeFileAllData(args.output_filepath, output_datalist2)
