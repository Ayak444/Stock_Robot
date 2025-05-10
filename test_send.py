import yfinance as yf
import pandas as pd
import requests
from datetime import datetime

# ----------- LINE Bot 設定 ------------
CHANNEL_ACCESS_TOKEN = "ywU3tBDTqR9bu5YsmQJXw3RT3cr5ZNPB9YbTnPYXPJZwmel4DaiXfWyeN5V7rIs1DHrt/uetsjI7NFYmTGdyWlRfCk5RDPGdzvYhgXxzn0q7iEtvLvOeEF+slxlkPPO/neD3Rf8DRTM+mLp2rkDjGgdB04t89/1O/w1cDnyilFU="
USER_ID = "C34abf9f270aa9a7c838371ed54db7f40"
# -------------------------------------

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"
}


def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def get_stock_data(ticker="0050.TW"):
    df = yf.download(ticker, period="2y", interval="1d", auto_adjust=True)
    
    # 檢查數據是否為空
    if df.empty:
        raise ValueError(f"No data found for {ticker}")

    df.dropna(inplace=True)

    if df.empty:
        raise ValueError(f"DataFrame for {ticker} is empty after removing NaNs")

    df["MA5"] = df["Close"].rolling(window=5).mean()
    df["MA20"] = df["Close"].rolling(window=20).mean()
    df["EMA5"] = df["Close"].ewm(span=5).mean()
    df["EMA20"] = df["Close"].ewm(span=20).mean()
    df["DIF"] = df["Close"].ewm(span=12).mean() - df["Close"].ewm(span=26).mean()
    df["DEA"] = df["DIF"].ewm(span=9).mean()
    df["MACD"] = df["DIF"] - df["DEA"]

    low_min = df['Low'].rolling(window=9).min()
    high_max = df['High'].rolling(window=9).max()
    rsv = (df['Close'] - low_min) / (high_max - low_min) * 100
    df['K'] = rsv.ewm(com=2).mean()
    df['D'] = df['K'].ewm(com=2).mean()

    df['RSI'] = calculate_rsi(df['Close'], period=14)

    return df



def score_strategy(df):
    if df.empty:
        raise ValueError("DataFrame is empty, no data available for analysis.")
    latest = df.iloc[-1]
    score = 0
    explanation = []


    ma5 = float(latest["MA5"])
    ma20 = float(latest["MA20"])
    ema5 = float(latest["EMA5"])
    ema20 = float(latest["EMA20"])
    dif = float(latest["DIF"])
    dea = float(latest["DEA"])
    k = float(latest["K"])
    d = float(latest["D"])
    rsi = float(latest["RSI"])

    if ma5 > ma20:
        score += 1
        explanation.append("MA5 > MA20 ✅")
    else:
        explanation.append("MA5 <= MA20 ❌")

    if ema5 > ema20:
        score += 1
        explanation.append("EMA5 > EMA20 ✅")
    else:
        explanation.append("EMA5 <= EMA20 ❌")

    if dif > dea:
        score += 1
        explanation.append("MACD 金叉 ✅")
    else:
        explanation.append("MACD 死叉 ❌")

    if k > d and k < 80:
        score += 1
        explanation.append("KD 金叉 ✅")
    elif k < d and k > 80:
        score -= 1
        explanation.append("KD 死叉 ❌")
    else:
        explanation.append("KD 無明顯訊號 ⚠️")

    if rsi < 30:
        score += 1
        explanation.append("RSI < 30 超賣 ✅")
    elif rsi > 70:
        score -= 1
        explanation.append("RSI > 70 超買 ❌")
    else:
        explanation.append("RSI 中性 ⚠️")

    if score >= 4:
        suggestion = "✅ 強烈建議買入"
    elif score >= 2:
        suggestion = "📈 可觀察進場"
    elif score == 1:
        suggestion = "🔁 觀望"
    else:
        suggestion = "📉 建議賣出"

    return score, suggestion, explanation


def send_line_message(message):
    payload = {
        "to": USER_ID,
        "messages": [{"type": "text", "text": message}]
    }
    res = requests.post("https://api.line.me/v2/bot/message/push", headers=headers, json=payload)
    return res.status_code, res.text


def run_analysis(tickers=["0050.TW", "2618.TW","2330.TW"]):
    all_messages = []
    today = datetime.today().strftime("%Y-%m-%d")

    # 自訂名稱對應
    name_map = {
        "0050.TW": "台灣50 (0050)",
        "2618.TW": "長榮航 (2618)",
        "2330.TW": "台積電(2330)"
    }

    for ticker in tickers:
        try:
            df = get_stock_data(ticker)
            score, suggestion, explanation = score_strategy(df)

            stock_name = name_map.get(ticker, ticker)

            message = f"[{stock_name} 技術分析 - {today}]\n"
            message += "\n".join(explanation)
            message += f"\n\n綜合分數：{score} 分\n建議：{suggestion}"
            all_messages.append(message)
        except Exception as e:
            all_messages.append(f"[{ticker}] 分析失敗：{str(e)}")

    full_message = "\n\n====================\n\n".join(all_messages)
    status, response = send_line_message(full_message)
    print("發送狀態：", status)
    print("LINE 回應：", response)


if __name__ == "__main__":
    run_analysis(["0050.TW", "2618.TW","2330.TW"])
