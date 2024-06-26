# stretch-emotion

## ファイル構成
- stretch_emotion
  - コード実態をおいているフォルダ
- requirements.txt
  - ミドルウェアを動かす上で必要になるライブラリ情報を適宜追加していく

### stretch_emotion以下について
- Core.py
  - いろんな低アプリケーション層からくる感情値を変換するための処理本体
  - ミドルウェアのコア実装はここに追加していく

- DBUtil.py
  - MySQLに接続する、操作するための関数をまとめたコード
  - DBUtil.pyのインストラクタに直接接続先情報は書き込む構成にしてある
  - 基本的にCore.py内で呼び出して使う

- FileOperator.py
  - ファイル操作に関する関数をまとめたコード
  - readCSVFile 
    - CSVファイルに特化した読み込み関数
  - readFile
    - とりあえずタブ切り分けされた文字列入ったファイル読む関数
  - writeFileSingleData
    - 1データだけファイルに書き込む関数。aのため、追記

  - writeFileAllData
    - リストを渡すとリストの中身を全てファイルに書き込む関数。wのため、上書き

- Queries.txt
  - MySQLに予め作っておく必要があるテーブル群の作成クエリ

- debug.py
  - Core.pyの動作を確認するためのプログラム
  - ファイル読み込み出力対応のため、コマンドライン引数を受け取る
  - ```python3 debug.py 入力ファイルパス 出力ファイルパス```

## DBのテーブル構成について
- - base_emotionテーブル
    - emotion_stretchによって最終的に出力される分類結果に関するテーブル
- カラム設計
  - base_id (primary_key, auto_increment)
  - emotion

- emotion_modelテーブル
  - 変換ターゲットとなる感情モデル(様々に入力される)ものの情報テーブル
  - model_id (primary_key, auto_increment)
  - model_name

- target_emotionモデル
  - 変換ターゲットとなる感情モデルそれぞれが持つモデル感情の参照テーブル

- model_name (primary_key)
  - emotion_id (primary_key)
  - emotion (感情値を記載する)

- ruleテーブル
  - base_emotionとtarget_emotion間の変換ルールをまとめたテーブル
  - model_id (primary_key)
  - base_id (forgin_key)
  - model_emotion
- rassel_emotions_ruleテーブル
  - これが感情変換のキモになるテーブル
  - target_emotionが持つemotionの内容は必ずrasel_emotions_ruleのemotionのいずれかに一致しなければならない
  - 一致したemotionを予め決めたruleに従ってbase_emotionのemotionに変換する
  - Id (primary key)
  - emotion (target_emotionのemotionと一致する)
  - base_id (対応するbase_emotion_id)

## Core.pyについて
- stretchEmotion関数を呼び出す
- DB上に予め登録されたルールに従って感情変換された結果を返す
  - 引数
    - model_name(使用元の感情推定モデル名)
    - emotion(使用元の感情推定モデルが出した感情(テキスト))
    - emotion_id(使用元の感情推定モデルが出したemotion_id)
    - accuracy(もし精度で使うか判断するなら使う)

  - 戻り値 (現状は２変数で戻す)
    - emotion_id
    - emotion_name

- 内部的なヘルパー関数として以下のものを持つ
  - emotionTransfer
    - 実際の感情変換を行う関数
  - addRuleEmotionTransfer
    - 既存のルールがDB上に存在しない場合、rassel_emotions_ruleとの対応に従って新しくルールを追加する関数
  - emotionTransferW2V
    - 予め4象限に対応するする比較単語("excited", "angry", "sad", "serene")と入力された感情単語のコサイン類似度を比較して一番大きい値の象限番号と比較単語を返す
