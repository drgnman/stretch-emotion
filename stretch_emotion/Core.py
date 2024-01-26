from DBUtil import DBUtil

class Core:

    def __init__(self):
        self.db = DBUtil()
        self.db.createDBConnection()

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
            f"SELECT em.model_id, (SELECT base_id FROM rassel_emotions_rule WHERE emotions = '{emotion}') AS base_id, {emotion_id} "
            "FROM emotion_models em "
            f"WHERE em.model_name = '{model_name}';"
        )
        if (not self.db.executeQuery(query)): return "Add Rule Error"

        return True 

    # 残タスク: 精度によるデータ使用、もしくは破棄するような関数も作る必要ある？
    # 感情モデル変換全体の関数
    def stretchEmotion(self, model_name, emotion_id, emotion=""):
        # 感情モデルの存在確認
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

        # 感情モデル内の感情の存在確認
        query = f"SELECT emotion_id FROM target_emotions WHERE model_name = '{model_name}' AND emotion_id = '{emotion_id}';"
        result = self.db.fetchSingleQuery(query)
        # もしデータがなかったら追加処理を行う
        if len(result) ==  0:
            if(not self.addRuleEmotionTransfer(model_name, emotion_id, emotion)):
                return "Add Rule Function Error"
        # 変換処理の実行
        return self.emotionTransfer(model_name, emotion_id)
