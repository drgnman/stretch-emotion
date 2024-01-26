from Core import Core

test_module = Core()
emotion_id, emotion_name = test_module.stretchEmotion("テスト感情3", 1, "覚醒")
print("調整後の感情ID: ", emotion_id)
print("調整後の感情: ", emotion_name)
