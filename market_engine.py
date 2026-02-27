import yfinance as yf
import pandas as pd
import requests
import feedparser
from datetime import datetime, timedelta

# =========================
# TELEGRAM SETTINGS
# =========================
BOT_TOKEN = "8600534484:AAGicx-taC1qLc2nRG17dxN9Pw-Y1NBecXg"
CHAT_ID = "585008735"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": message})
    except:
        pass

# =========================
# CUSTOM WATCHLIST
# =========================
WATCHLIST = [
    "RELIANCE.NS",
    "TATAMOTORS.NS",
    "HDFCBANK.NS",
    "HDFCAMC.NS",
    "ANGELONE.NS",
    "BSE.NS",
    "ALPEXSOLAR.NS"
]

# =========================
# 1️⃣ PRICE + VOLUME ALERTS
# =========================
def price_volume_alerts():

    alerts = []

    for stock in WATCHLIST:
        try:
            df = yf.download(stock, period="30d", interval="1d", progress=False)

            if df.empty or len(df) < 21:
                continue

            latest_close = float(df["Close"].iloc[-1])
            prev_close = float(df["Close"].iloc[-2])
            latest_volume = float(df["Volume"].iloc[-1])
            avg_volume = float(df["Volume"].rolling(20).mean().iloc[-2])

            pct_change = ((latest_close - prev_close) / prev_close) * 100

            if abs(pct_change) >= 3:
                alerts.append(f"{stock} moved {pct_change:.2f}%")

            if avg_volume > 0 and latest_volume >= 5 * avg_volume:
                multiple = latest_volume / avg_volume
                alerts.append(f"{stock} volume spike {multiple:.1f}x")

        except:
            continue

    return alerts

# =========================
# 2️⃣ DIVIDENDS
# =========================
def dividend_alerts():

    div_alerts = []

    for stock in WATCHLIST:
        try:
            ticker = yf.Ticker(stock)
            dividends = ticker.dividends

            if not dividends.empty:
                last_div_date = dividends.index[-1]
                last_div_value = dividends.iloc[-1]

                if (datetime.now() - last_div_date.to_pydatetime()).days <= 7:
                    div_alerts.append(f"{stock} dividend declared ₹{last_div_value}")

        except:
            continue

    return div_alerts

# =========================
# 3️⃣ FII / DII DATA
# =========================
def fii_dii_data():

    try:
        date_str = datetime.now().strftime("%d%m%Y")
        url = f"https://archives.nseindia.com/content/fo/fo_{date_str}.csv"

        df = pd.read_csv(url)

        fii = df[df["Client Type"] == "FII"]["Net Amount"].sum()
        dii = df[df["Client Type"] == "DII"]["Net Amount"].sum()

        return f"FII: {fii:.0f} | DII: {dii:.0f}"

    except:
        return "FII/DII data not available yet"

# =========================
# 4️⃣ MARKET NEWS
# =========================
def market_news():

    rss_feeds = [
        "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
        "https://www.business-standard.com/rss/markets-106.rss"
    ]

    headlines = []

    for url in rss_feeds:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:2]:
                headlines.append(entry.title)
        except:
            continue

    return headlines[:4]

# =========================
# MAIN EXECUTION
# =========================
if __name__ == "__main__":

    sections = []

    # Price + Volume
    pv = price_volume_alerts()
    if pv:
        sections.append("🚨 PRICE / VOLUME ALERTS\n" + "\n".join(pv))

    # Dividends
    divs = dividend_alerts()
    if divs:
        sections.append("💰 DIVIDENDS\n" + "\n".join(divs))

    # FII/DII
    fii_dii = fii_dii_data()
    sections.append("📊 FII / DII\n" + fii_dii)

    # News
    news = market_news()
    if news:
        sections.append("📰 MARKET NEWS\n" + "\n".join(news))

    if not sections:
        sections.append("No major updates currently.")

    message = "📢 MARKET ENGINE ALERT\n\n" + "\n\n".join(sections)

    send_telegram(message)

    print("✅ Full market engine update sent")