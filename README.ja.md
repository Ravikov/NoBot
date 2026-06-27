# NoBot

📖 日本語 | [English](./README.md) | [简体中文](./README.zh-CN.md)

**具身AI** エージェントプラットフォーム。LLM による会話と物理ハードウェア制御を融合。マルチモデル構成、長期記憶、マルチユーザー分離に対応し、WebSocket 経由で実機（ESP32）と接続、AI をスクリーンから現実世界へ拡張します。

> 初めての本格的なプログラミングプロジェクトです。至らぬ点もあるかと思いますが、ご助言いただければ幸いです！

---

## クイックスタート

**Python ≥ 3.10**

```bash
git clone https://github.com/Ravikov/NoBot.git
cd NoBot
python -m venv .venv

# Windows:
.venv\Scripts\pip install -r requirements.txt
# Linux / macOS:
.venv/bin/pip install -r requirements.txt

python main.py
```

初回起動時に設定ウィザードが起動し、各モデルの URL・API Key・モデル名を対話的に設定します。設定は `nobot/config/<ユーザー名>/config.json` に保存されます。

### クイック起動

| プラットフォーム | 方法 |
|---|---|
| Windows | `Run.bat` をダブルクリック |
| Linux / macOS | ターミナルで `./Run.sh` |

---

## マルチユーザーシステム

NoBot は複数の独立したユーザーをサポート。各ユーザーは以下を持ちます：

- **API 設定**（`nobot/config/<ユーザー名>/`）
- **記憶と会話履歴**（`nobot/memory/<ユーザー名>/`）
- **ClawBot セッション**（`IMchat/clawbot/config/<ユーザー名>/`）

起動時にユーザーを選択、作成、削除できます（`main` ユーザーは削除不可）。

---

## 起動モード

| # | モード | 説明 |
|---|---|---|
| 1 | Webhook | Flask サーバー（`:5000`） |
| 2 | CLI | ターミナルで直接入力 |
| 3 | 微信個人アカウント | ⏳ 現在利用不可 |
| **4** | **微信 ClawBot** | ✅ **推奨** — QR コードスキャンで自動送受信 |
| **5** | **WebSocket** | ✅ WebSocket サーバー（`ws://127.0.0.1:7323`）— カスタムクライアント（ESP32 含む） |
| **6** | **WebSocket + ClawBot** | ✅ **微信から ESP32 制御** — ClawBot + WebSocket 同時起動 |

---

## ESP32 / ハードウェア連携（NoBot-esp32）

NoBot は WebSocket 経由で ESP32-S3（[NoBot-esp32](https://github.com/Ravikov/NoBot-esp32-demo) ファームウェア）を制御し、LED・ブザー・モーターなどの物理ハードウェアを操作できます。

### アーキテクチャ

```
┌──────────────────── NoBot ────────────────────┐
│  WeChat / CLI  ──►  LLM Core  ──►  Reply      │
│                               │    Engine      │
│                        WebSocket Server :7323  │
└───────────────────────┬───────────────────────┘
                        │  JSON コマンド
┌───────────────── ESP32-S3 (NoBot-esp32) ──────┐
│  WiFi ──► Command Handler ──► GPIO (LED/Motor) │
└───────────────────────────────────────────────┘
```

### 動作の流れ

1. **NoBot 起動** — モード **5**（WebSocket のみ）または **6**（微信 + ESP32）
2. **ESP32 接続** — WebSocket サーバーに接続、使用可能なアクションとハードウェアを報告
3. **ユーザーが指示** — 微信・CLI・WebSocket 経由で送信
4. **LLM が判断** — どのアクションをどのハードウェアで実行するか決定
5. **JSON コマンド** を ESP32 に送信：`{"action":0, "hardware":0}`
6. **ESP32 実行** — GPIO 制御、LED 点滅など

### 設定

初回起動時に **`embodiment`** ユーザー（タイプ `esp32`）が自動生成されます。

各エンティティユーザーは以下を持ちます：

| ファイル | 説明 |
|---|---|
| `nobot/config/embodiment/config.json` | API 設定 |
| `nobot/config/embodiment/soul.md` | ハードウェア制御用システムプロンプト |
| `nobot/config/embodiment/actionAndHardware.txt` | ESP32 が報告する能力テーブル（自動生成） |

制御時の LLM 応答形式：

```json
{"msg":"完了！","action":0,"hardware":0}
```

詳細は [doc/embodiment-zh.md](./doc/embodiment-zh.md) をご参照ください。

---

## クイックコマンド

| コマンド | 効果 |
|---|---|
| `/rememory` | 現在のユーザーの会話記憶をクリア |
| `/memory` | 即時記憶要約を実行 |
| `/rehistory` | 長期履歴アーカイブをクリア |

---

## 機能ステータス

| 機能 | 状態 | 備考 |
|---|---|---|
| テキストメッセージ送受信 | ✅ | 対応済み |
| 画像受信 + AI マルチモーダル | ✅ | 自動ダウンロード・AES復号、マルチモーダルモデルで描写 |
| 動画受信 (type 5) | ✅ | ダウンロード後、画像と同様に処理 |
| メッセージバッチ処理 (type 9) | ✅ | 複数メッセージを蓄積後に LLM 呼び出し |
| スマート待機（LLM 判断） | ✅ | 補助モデルが最適な蓄積時間を予測 |
| ロングポーリングリアルタイム受信 | ✅ | 対応済み |
| QR コードログイン | ✅ | 対応済み |
| スマート検索判断 | ✅ | 補助モデルが検索要否を判断 |
| マルチユーザー | ✅ | 独立した設定・記憶・ClawBot セッション |
| 時間注入 | ✅ | 現在時刻を LLM コンテキストに注入（オプション） |
| リピートモード | ✅ | 入力メッセージをそのまま返信 |
| 画像・動画送信 | ❌ | iLink プロトコル確認後対応予定 |
| 微信個人アカウント (itchat) | ❌ | 公式プロトコル制限により利用不可 |

---

## 設定

### 設定ウィザード（`set`）

1. **検索機能の有効/無効** — `or_search`
2. **各モデルの API 情報**：
   - **メインモデル**（`API`）— 応答生成用 LLM
   - **補助モデル**（`secAPI`）— 検索判断・スマート待機用
   - **検索モデル**（`searchAPI`）— 検索機能付き LLM
   - **マルチモーダルモデル**（`multimodalAPI`）— 画像・動画理解用
3. **メインモデルパラメータ**：
   - `temperature`（0〜2、デフォルト 1.0）
   - `max_history_turns`（デフォルト 20）
   - `or_time_feel` — 時間注入の有効/無効

主な設定項目は [doc/configuration-zh.md](./doc/configuration-zh.md) をご参照ください。

---

## プロジェクト構造

```
NoBot/
├── main.py                              # エントリーポイント
├── nobot/                               # コアロジック
│   └── src/
│       ├── common.py                    # パス・設定・デフォルト値
│       ├── guide.py                     # 設定ウィザード
│       ├── core/
│       │   ├── reply/reply.py           # ReplyHandler
│       │   ├── reply/touch_llm.py       # LLM API 呼び出し
│       │   └── mem/memory.py            # 記憶圧縮
│       └── user/user.py                 # マルチユーザーシステム
├── websocket/server.py                  # WebSocket サーバー
├── IMchat/clawbot/                      # 微信 ClawBot 実装
├── doc/                                 # 詳細ドキュメント
└── debug/                               # ログ・デバッグ
```

---

## 注意事項

- `debug/bot.log` に全ターミナル出力が記録されます。起動メニューで `del` を実行するか、自動クリーンアップに委ねてください。
- システムプロンプトは `nobot/config/<ユーザー名>/soul.md` を編集してカスタマイズ。
- 設定ファイルが壊れた場合は削除してください。次回起動時にデフォルト設定が自動生成されます。
- バグ報告や提案は [Issue](https://github.com/Ravikov/NoBot/issues) へどうぞ！🎉
