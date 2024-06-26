import gensim
import gensim.downloader as api
from DBUtil import DBUtil

class Core:
    def __init__(self):
        self.db = DBUtil()
        self.db.createDBConnection()
        self.model = api.load("word2vec-google-news-300")
        # self.model = gensim.models.Word2Vec.load("/Users/drgnman/Downloads/latest-ja-word2vec-gensim-model/word2vec.gensim.model")
        self.base_quadrants = ["excited", "angry", "sad", "serene"] # 1象限、2象限, 3象限, 4象限
    # DB上に設定された変換ルールに則って実際に変換するコード
    # 変換はMySQL上で対応する基礎感情コードを取得することで行なっている
    # 戻り値: 変換後の感情ID(emotion_id)、感情名(emotion)
    def emotionTransfer(self, model_name, emotion_id):
        query = (
            "SELECT be.id, " 
            "    be.emotion "  
            "FROM"
            "    emotion_models em "
            "JOIN"
            "    target_emotions te ON em.model_name = te.model_name "
            "JOIN"
            "    rule r ON em.model_id = r.model_id AND te.emotion_id = r.emotion_id "
            "JOIN "
            "    base_emotions be ON r.base_id = be.id "
            "WHERE "
            f"    em.model_name = '{model_name}' AND te.emotion_id = {emotion_id};"
        )
        result = self.db.fetchSingleQuery(query)
        emotion_id, emotion = result
        return emotion_id, emotion

    # 感情変換のルールがDB上になかった場合にDB上に新しく変換ルールを追加するコード
    # モデル自体の追加は処理本体で行わせる
    # 1. target_emotionsテーブルにモデルが持つ感情要素を全て追加
    # 2. rassel_emotions_ruleに則って対応する基礎4感情との紐付けを行なったものをruleテーブルに追加する
    # 制約: rassel_emotions_rule上にない感情単語の場合、記録できない
    def addRuleEmotionTransfer(self, model_name, emotion_id, emotion):
        query = ("INSERT INTO target_emotions (model_name, emotion_id, emotion)"
            f"VALUES ('{model_name}', {emotion_id}, '{emotion}');"
        )
        if (not self.db.executeQuery(query)): return "Add Emotion Error"

        query = ("INSERT INTO rule (model_id, base_id, emotion_id) "
            f"SELECT em.model_id, (SELECT base_id FROM rassel_emotions_rule WHERE emotion = '{emotion}') AS base_id, {emotion_id} "
            "FROM emotion_models em "
            f"WHERE em.model_name = '{model_name}';"
        )
        if (not self.db.executeQuery(query)): return "Add Rule Error"

        return True 

    # word2vecを用いたコサイン類似度から4象限の推定を行う関数
    def emotionTransferW2V(self, emotion_name):
        index, max_similarity = 0, 0.0
        if (emotion_name == "Joy" or emotion_name == "joyful"):
          return str(index+1), self.base_quadrants[1]
        if (emotion_name == "surprised"):
           return str(index+1), self.base_quadrants[0] 
        u_emotion_name = emotion_name.lower()
        for i in range(len(self.base_quadrants)):
            similarity = self.model.similarity(u_emotion_name, self.base_quadrants[i])
            # print("emotion: ", self.base_quadrants[i], ",similarity: ", similarity)
            if (max_similarity < similarity):
                max_similarity = similarity 
                index = i
        return str(index+1), self.base_quadrants[index]

    # 残タスク: 精度によるデータ使用、もしくは破棄するような関数も作る必要ある？
    # 多分, こんな感じ 感情ごとでやる必要があるか、モデル単位でいいかは検出器の結果を見て要検討
    # def judgeModelThreshold(self, threshold, accuracy):
    #     if threshold > accuracy: return False
    # return True
    
    # 感情モデル変換全体の関数
    # def stretchEmotion(self, model_name, emotion_id, emotion="", accuracy=0):
    def stretchEmotion(self, model_name, emotion="", emotion_id=0):
        mode = True

        # Word2Vecを用いて感情変換した結果を返す
        if mode:
            return self.emotionTransferW2V(emotion)

        # ルールベースで感情変換した結果を返す
        else:
            # 感情モデルの存在確認
            # thresholdはまだ未対応
            # query = f"SELECT model_id, threshold FROM emotion_models WHERE model_name = '{model_name}';"
            query = f"SELECT model_id FROM emotion_models WHERE model_name = '{model_name}';"
            result = self.db.fetchSingleQuery(query)
            if len(result) == 0:
                query = ("INSERT INTO emotion_models (model_name) "
                    f"SELECT * FROM (SELECT '{model_name}') AS tmp "
                    "WHERE NOT EXISTS ("
                    f"    SELECT model_id FROM emotion_models WHERE model_name = '{model_name}' "
                    ") LIMIT 1;"
                )
                if(not self.db.executeQuery(query)): return "Add Emotion Model Error"

            # 精度が閾値より下の場合値を使わずに処理を終了
            # if not judgeModelThreshold(result[1], accuracy): return "", ""

            # 感情モデル内の感情の存在確認
            query = f"SELECT emotion_id FROM target_emotions WHERE model_name = '{model_name}' AND emotion_id = '{emotion_id}';"
            result = self.db.fetchSingleQuery(query)
            # もしデータがなかったら追加処理を行う
            if len(result) ==  0:
                if(not self.addRuleEmotionTransfer(model_name, emotion_id, emotion)):
                    return "Add Rule Function Error"
            # 変換処理の実行
            return self.emotionTransfer(model_name, emotion_id)
