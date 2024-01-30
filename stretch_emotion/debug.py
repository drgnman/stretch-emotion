import argparse
import copy
from Core import Core
from FileOperator import FileOperator

parser = argparse.ArgumentParser()
parser.add_argument("input_filename", help="input file name")
parser.add_argument("output_filepath", help="output file path")

args = parser.parse_args()

# ファイル操作用、感情変換用のクラスオブジェクトを生成
fo = FileOperator()
core = Core()
 
# ファイルの読み込みと、出力リスト用のハードコピー
datalist = fo.readCSVFile(args.input_filename)
output_datalist = copy.copy(datalist)


# 感情変換
for i in range(len(datalist)):
    output_datalist[i][1], output_datalist[i][2] = core.stretchEmotion(args.input_filename, datalist[i][1], datalist[i][2])
    print("発話ID: ", output_datalist[i][0],"調整後の感情ID: ", output_datalist[i][1], "調整後の感情名: ", output_datalist[i][2])

# 結果書き出し
fo.writeFileAllData(args.output_filepath, output_datalist)
