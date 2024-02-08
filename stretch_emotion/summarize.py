import argparse
from FileOperator import FileOperator

import math
import spacy

from pysummarization.nlpbase.auto_abstractor import AutoAbstractor
from pysummarization.tokenizabledoc.mecab_tokenizer import MeCabTokenizer
from pysummarization.abstractabledoc.top_n_rank_abstractor import TopNRankAbstractor

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.luhn import LuhnSummarizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.summarizers.text_rank import TextRankSummarizer

fo = FileOperator()

# sumy の sumy.nlp.tokenizers.Tokenizerに似せた、オリジナルのTokenizerを定義
#   https://github.com/miso-belica/sumy/blob/master/docs/how-to-add-new-language
## うまくいかない感じ
# nlp = spacy.load('ja_ginza')
# class myTokenizer:
#     @staticmethod
#     def to_sentences(text) :
#         return [str(s) for s in nlp(text).sents] # spaCyは、「sents」で文のジェネレータを戻す
# 
#     @staticmethod
#     def to_words(sentence) :
#         l = next(nlp(sentence).sents).lemma_  # spaCyは、「lemma_」で文のレンマ化した文字列を戻す
#         return l.split(' ')  # spacy/GiNZAの仕様により、半角スペース区切りでトークン化されるようなのでそれを前提にリストにする

# pysummarizationの初期化
auto_abstractor = AutoAbstractor()
auto_abstractor.tokenizable_doc = MeCabTokenizer()
auto_abstractor.delimiter_list = ["。", "\n"]
abstractable_doc = TopNRankAbstractor()

parser = argparse.ArgumentParser()
parser.add_argument("input_filename", help="input file name")

args = parser.parse_args()

datalist = fo.readCSVFile(args.input_filename)

# 象限の定義
EXCITED = 1
ANGRY = 2
SAD = 3
SERENE = 4 

FIRST_SUMY_COUNT = 10
ONE_TEXT_COUNT = 2 
LAST_SUMY_COUNT = 5

# datalist = fo.readCSVFile("/Users/drgnman/Desktop/trans.csv")
datalist = [row[:1] + [int(row[1])] + row[2:] for row in datalist]

# print(datalist[0])
textlist = []
text = ""
counter = 0
# 感情象限の変化に伴う文章整理
for i in range(len(datalist)-1):
    # 落ち着いた感情に移る時は結論を話しているはず
    # if ((counter > ONE_TEXT_COUNT) and (datalist[i][1] == ANGRY and datalist[i+1][1] == SERENE) or 
    #     (datalist[i][1] == ANGRY and datalist[i+1][1] == SAD) or
    #     (datalist[i][1] == EXCITED and datalist[i+1][1] == SAD) or
    #     (datalist[i][1] == EXCITED and datalist[i+1][1] == SERENE)):
    #     text += datalist[i][3]
    #     if (text[:-2] != "。"):
    #       text += "。"
    #     textlist.append(text)
    #     text = ""
    # # 興奮感情に移る時は新しい議題を話しているはず
    # elif ((counter > ONE_TEXT_COUNT) and (datalist[i][1] == SERENE and datalist[i+1][1] == ANGRY) or 
    #     (datalist[i][1] == SERENE and datalist[i+1][1] == EXCITED) or 
    #     (datalist[i][1] == SAD and datalist[i+1][1] == ANGRY) or 
    #     (datalist[i][1] == SAD and datalist[i+1][1] == EXCITED)):
    #     if (text[:-2] != "。"):
    #       text += "。"
    #     textlist.append(text)
    #     text = datalist[i][3]
    # else:
    #     if (counter > ONE_TEXT_COUNT): 
    #         if (text[:-2] != "。"):
    #           text += "。"
    #         counter = 0
    #     else:
    #         text += datalist[i][3] + "、"
    #     counter += 1

    if (datalist[i][1] != datalist[i+1][1]):
        text = datalist[i][3]+"。"
        textlist.append(text)

# print(textlist)
summary_list = []

# テキスト結合するとうまく動かなくなる
group_size = 1 

textlist = [item for item in textlist if item != "。"]
texts = ['。'.join(textlist[i:i + group_size]) for i in range(0, len(textlist), group_size)]

# print(texts)

# for i in range(len(textlist)):
#     print(textlist[i])

# 抽出された文章群ごとに一回、sumyを用いて要約
for i in range(len(texts)):
    parser = PlaintextParser.from_string(texts[i], Tokenizer("japanese"))
    # parser = PlaintextParser.from_string(textlist[i], myTokenizer())

    summarizer =LuhnSummarizer()

    first_sumy_count = math.ceil(len(textlist[i]) * 0.2)
    # テキストの要約
    # summary = summarizer(parser.document, FIRST_SUMY_COUNT)  # 分量は調整必要 
    summary = summarizer(parser.document, first_sumy_count)  # 分量は調整必要 
    if (summary != ()):
        # print('\n'.join([sentence._text for sentence in summary]))
        summary_list.append([str(sentence) for sentence in summary])

# print("first summary")
# for i in range(len(summary_list)):
#     print("".join(summary_list[i]))
# # 一旦要約された文章群に対して、pysummarizationを用いて重要度の高い順に整理
final_summary = ""
for item in summary_list:
    base_summary_text = "。".join(item)
    result_dict = auto_abstractor.summarize(base_summary_text, abstractable_doc)

    sum_text = ''
    # print(base_summary_text)
    for i in range(3): # 1番高いものだけだと減りすぎかなと思って3つ目まで、要調整
        if (i < len(result_dict["summarize_result"])):
            final_summary += str(result_dict["summarize_result"][i])

final_summary = ""
for item in summary_list:
    final_summary += "".join(item)

# pysummarizationによって重要度順にされたリストを文章に結合
# 最終的な要約
re_summary = "".join(final_summary.split("\n"))
parser = PlaintextParser.from_string(re_summary, Tokenizer("japanese"))
# print("LuhnSummarizer")
summarizer = LuhnSummarizer()
# テキストの要約
summary = summarizer(parser.document, LAST_SUMY_COUNT)  # 2文で要約
if (summary != ()):
    print('\n'.join([sentence._text for sentence in summary]))

# print("LexRankSummarizer")
# summarizer = LexRankSummarizer()
# # テキストの要約
# summary = summarizer(parser.document, 5)  # 2文で要約
# if (summary != ()):
#     print('\n'.join([sentence._text for sentence in summary]))
# 
# print("LsaSummarizer")
# summarizer = LsaSummarizer()
# # テキストの要約
# summary = summarizer(parser.document, 5)  # 2文で要約
# if (summary != ()):
#     print('\n'.join([sentence._text for sentence in summary]))
# 
# print("TextRankSummarizer")
# summarizer = TextRankSummarizer()
# # テキストの要約
# summary = summarizer(parser.document, 5)  # 2文で要約
# if (summary != ()):
#     print('\n'.join([sentence._text for sentence in summary]))
