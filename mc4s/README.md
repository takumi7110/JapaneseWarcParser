# mc4データセットをクリーニングするスクリプト
- Huggingfaceのdatasetsから読み込み
    - 各レコードごとに
        - 正規化
        - 文章クリーニング
        - 機械学習による選別(教師有り)
        - 記事内容のクラス分け(教師なし) 
        - 出力