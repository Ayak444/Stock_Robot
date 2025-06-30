# 📈 股票技術分析 LINE 通知機器人

這是一個使用 Python 製作的股票技術分析機器人，能透過 LINE Notify 向指定使用者即時推送分析結果。分析指標包含：均線 (MA/EMA)、MACD、KD 指標與 RSI，幫助你快速掌握買賣時機。

## 🚀 功能簡介

- 使用 `yfinance` 抓取台股每日資料（如 0050、2330、2618）。
- 計算常用技術指標：
  - MA5 / MA20
  - EMA5 / EMA20
  - MACD（金叉 / 死叉）
  - KD 指標（金叉 / 死叉）
  - RSI（超買 / 超賣）
- 自動評分與文字建議
- 將結果推送至你的 LINE Bot

## 📦 安裝步驟

```bash
git clone https://github.com/yourusername/stock-line-bot.git
cd stock-line-bot
pip install -r requirements.txt
```
## 🛠 使用技術

- Python 3.x
- [yfinance](https://pypi.org/project/yfinance/)
- [pandas](https://pandas.pydata.org/)
- LINE Messaging API (`push` 模式)

## ⚙️ 使用方式
前往 LINE Developers 建立 Channel，取得 Channel Access Token。

查詢你的 LINE User ID 並填入以下欄位：
CHANNEL_ACCESS_TOKEN = "你的 Channel Access Token"
USER_ID = "你的 LINE User ID"

## 📊 範例訊息
[台積電(2330) 技術分析 - 2025-06-30]
MA5 > MA20 ✅
EMA5 > EMA20 ✅
MACD 金叉 ✅
KD 金叉 ✅
RSI 中性 ⚠️

綜合分數：4 分
建議：✅ 強烈建議買入

## 🔐 注意事項
此專案僅供學習與參考使用，不構成任何投資建議。

若抓取不到股價資料，請確認該股票代號正確，並確保網路暢通。
