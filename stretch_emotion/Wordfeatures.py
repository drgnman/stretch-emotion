import MeCab as MeCab

class Wordfeatures:
    def __init__(self):
        self.word_dic = ["じゃあ", "でも", "なんか", "?"]

    def judgeSpecificWords(self, words):
        # print("words: ", words)
        dic_path = "./jumandic"
        mecab = MeCab.Tagger(dic_path)
        parsed = mecab.parse(words)

        # 解析結果を行ごとに分割
        lines = parsed.split('\n')

        # print("lines: ", lines)
        # 解析結果から単語を抽出してリストに格納
        words_in_text = []
        for line in lines:
            # 行をタブで分割して、各部分を取得
            parts = line.split('\t')
            if len(parts) > 1:  # 形態素解析の結果の行は通常、2つ以上の部分に分かれている
                word = parts[0]  # 単語部分
                words_in_text.append(word)

        for word in words_in_text:
            for spcific in self.word_dic:
                if (word == spcific):
                    return words
        
        return ""