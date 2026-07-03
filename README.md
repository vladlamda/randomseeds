# Random Chunk Seeds データパック (Minecraft Java 26.2)

1チャンク（16×16ブロック）ごとにバイオームと地形がガラッと変わる、
「チャンクごとに別のシード値で生成されたような」ワールドを作るデータパックです。

## 内容

- **バイオーム**: 26.2 に存在する全 66 バイオーム（ネザー・エンド・洞窟バイオーム含む）を
  `multi_noise` 方式で完全ランダムに配置。気候パラメータ（temperature × humidity）の
  20×20=400 セルに66バイオームをシャッフルして割り当て、超高周波の気候ノイズで
  約1チャンクサイズのパッチ状にランダム選択されます。
  （チェッカーボード方式だと斜め一直線に同じバイオームが並ぶため、この方式に変更）
- **地形**: バニラの `overworld/offset` 密度関数に高周波ノイズ（`random_chunks:chunk_scramble`）を
  加算し、チャンク規模で標高が激しく上下するカオスな地形を生成します。
  （データパックのワールド生成では「本当にチャンクごとに独立したシード」は表現できないため、
  1〜2チャンク周期のノイズによる近似です）
- **構造物**: バニラの構造物設定はそのまま（要塞・寺院・トライアルチャンバーなどすべて生成されます）。
  村（5種）は全バイオームで生成可能になるようタグを上書きしているため、確実に見つかります。

## ファイル構成

```
random_chunk_seeds/
├── pack.mcmeta                                  (pack format 107 = 26.2)
└── data/
    ├── minecraft/
    │   ├── dimension/overworld.json             multi_noise (400セルの気候グリッド) に変更
    │   ├── worldgen/density_function/overworld/offset.json
    │   │                                        バニラのoffsetにスクランブルノイズを加算
    │   └── tags/worldgen/biome/has_structure/village_*.json
    │                                            村を全バイオームで生成可能に
    └── random_chunks/
        └── worldgen/
            ├── noise_settings/scrambled.json    バニラのコピー + 気候ノイズを高周波に差し替え
            ├── density_function/scramble_offset.json  地形スクランブルの強さ (0.75)
            └── noise/
                ├── chunk_scramble.json          地形用の高周波ノイズ (firstOctave -5)
                ├── biome_temperature.json       バイオーム用気候ノイズ (firstOctave -9)
                └── biome_humidity.json          バイオーム用気候ノイズ (firstOctave -9)
```

## 使い方

1. `random_chunk_seeds.zip`（または `random_chunk_seeds` フォルダごと）を用意する
2. **ワールド新規作成画面 → 「データパック」** でこのパックをドラッグ＆ドロップして有効化する
   （ワールド生成を変更するパックなので、**必ずワールド作成時に** 入れてください。
   作成済みワールドに後から入れても既存チャンクは変わりません）
3. 「実験的機能の警告」が出た場合はそのまま続行
4. ワールドを生成

## 調整方法

- 地形の暴れ具合: `data/random_chunks/worldgen/density_function/scramble_offset.json` の
  `argument1`（既定 `0.75`）を大きく/小さくする
- 変化の細かさ: `data/random_chunks/worldgen/noise/chunk_scramble.json` の
  `firstOctave`（既定 `-5`、`-4` にすると更に細かく激しく変化）
- バイオームパッチの大きさ: `biome_temperature.json` / `biome_humidity.json` の
  `firstOctave`（既定 `-9`）。`-10` にするとパッチが大きく、`-8` にすると細かくなる
  （変更後は `build_pack.py` の再実行は不要、直接編集でOK）

## 再生成

`build_pack.py` を実行すると、同梱のバニラ参照データ（`vanilla_offset_262.json` /
`biomes_262.json`）からデータパックのJSONを再生成できます。

```
python build_pack.py
```
