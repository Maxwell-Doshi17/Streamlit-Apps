import time
from dataclasses import dataclass
from typing import Dict, List, Optional
import pandas as pd
import requests
import streamlit as st


st.set_page_config(page_title="Crypto Arbitrage Scanner", layout="wide")


# =========================
# Config
# =========================
SYMBOL_OPTIONS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT"]
REFRESH_SECONDS_DEFAULT = 15
REQUEST_TIMEOUT = 8


@dataclass
class ExchangeQuote:
    exchange: str
    symbol: str
    bid: Optional[float]
    ask: Optional[float]
    last: Optional[float]
    fee_pct: float
    withdrawal_fee_usd: float
    error: Optional[str] = None


def safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


# =========================
# Public endpoints
# =========================
def fetch_binance(symbol: str, fee_pct: float, withdrawal_fee_usd: float) -> ExchangeQuote:
    url = "https://api.binance.com/api/v3/ticker/bookTicker"
    try:
        r = requests.get(url, params={"symbol": symbol}, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        data = r.json()
        return ExchangeQuote(
            exchange="Binance",
            symbol=symbol,
            bid=safe_float(data.get("bidPrice")),
            ask=safe_float(data.get("askPrice")),
            last=None,
            fee_pct=fee_pct,
            withdrawal_fee_usd=withdrawal_fee_usd,
        )
    except Exception as e:
        return ExchangeQuote("Binance", symbol, None, None, None, fee_pct, withdrawal_fee_usd, str(e))


def fetch_kraken(symbol: str, fee_pct: float, withdrawal_fee_usd: float) -> ExchangeQuote:
    kraken_map = {
        "BTCUSDT": "XBTUSDT",
        "ETHUSDT": "ETHUSDT",
        "SOLUSDT": "SOLUSD",
        "XRPUSDT": "XRPUSD",
        "ADAUSDT": "ADAUSD",
    }
    pair = kraken_map.get(symbol)
    try:
        if pair is None:
            raise ValueError(f"{symbol} not mapped for Kraken")
        url = "https://api.kraken.com/0/public/Ticker"
        r = requests.get(url, params={"pair": pair}, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        data = r.json()
        if data.get("error"):
            raise ValueError(str(data["error"]))
        result = data.get("result", {})
        first_key = next(iter(result))
        quote = result[first_key]
        return ExchangeQuote(
            exchange="Kraken",
            symbol=symbol,
            bid=safe_float(quote.get("b", [None])[0]),
            ask=safe_float(quote.get("a", [None])[0]),
            last=safe_float(quote.get("c", [None])[0]),
            fee_pct=fee_pct,
            withdrawal_fee_usd=withdrawal_fee_usd,
        )
    except Exception as e:
        return ExchangeQuote("Kraken", symbol, None, None, None, fee_pct, withdrawal_fee_usd, str(e))


def fetch_coinbase(symbol: str, fee_pct: float, withdrawal_fee_usd: float) -> ExchangeQuote:
    product_map = {
        "BTCUSDT": "BTC-USD",
        "ETHUSDT": "ETH-USD",
        "SOLUSDT": "SOL-USD",
        "XRPUSDT": "XRP-USD",
        "ADAUSDT": "ADA-USD",
    }
    product = product_map.get(symbol)
    try:
        if product is None:
            raise ValueError(f"{symbol} not mapped for Coinbase")
        url = f"https://api.exchange.coinbase.com/products/{product}/book"
        r = requests.get(url, params={"level": 1}, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        data = r.json()
        bid = None
        ask = None
        if data.get("bids"):
            bid = safe_float(data["bids"][0][0])
        if data.get("asks"):
            ask = safe_float(data["asks"][0][0])
        return ExchangeQuote(
            exchange="Coinbase",
            symbol=symbol,
            bid=bid,
            ask=ask,
            last=None,
            fee_pct=fee_pct,
            withdrawal_fee_usd=withdrawal_fee_usd,
        )
    except Exception as e:
        return ExchangeQuote("Coinbase", symbol, None, None, None, fee_pct, withdrawal_fee_usd, str(e))

def fetch_bybit(symbol: str, fee_pct: float, withdrawal_fee_usd: float) -> ExchangeQuote:
    try:
        url = "https://api.bybit.com/v5/market/tickers"
        r = requests.get(
            url,
            params={"category": "spot", "symbol": symbol},
            timeout=REQUEST_TIMEOUT
        )
        r.raise_for_status()
        data = r.json()

        ticker = data["result"]["list"][0]

        return ExchangeQuote(
            exchange="Bybit",
            symbol=symbol,
            bid=safe_float(ticker.get("bid1Price")),
            ask=safe_float(ticker.get("ask1Price")),
            last=safe_float(ticker.get("lastPrice")),
            fee_pct=fee_pct,
            withdrawal_fee_usd=withdrawal_fee_usd,
        )
    except Exception as e:
        return ExchangeQuote("Bybit", symbol, None, None, None, fee_pct, withdrawal_fee_usd, str(e))
    
def fetch_bitstamp(symbol: str, fee_pct: float, withdrawal_fee_usd: float) -> ExchangeQuote:
    bitstamp_map = {
        "BTCUSDT": "btcusd",
        "ETHUSDT": "ethusd",
        "SOLUSDT": "solusd",
        "XRPUSDT": "xrpusd",
        "ADAUSDT": "adausd",
    }

    pair = bitstamp_map.get(symbol)

    try:
        if pair is None:
            raise ValueError(f"{symbol} not mapped for Bitstamp")

        url = f"https://www.bitstamp.net/api/v2/ticker/{pair}/"
        r = requests.get(url, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        data = r.json()

        return ExchangeQuote(
            exchange="Bitstamp",
            symbol=symbol,
            bid=safe_float(data.get("bid")),
            ask=safe_float(data.get("ask")),
            last=safe_float(data.get("last")),
            fee_pct=fee_pct,
            withdrawal_fee_usd=withdrawal_fee_usd,
        )
    except Exception as e:
        return ExchangeQuote("Bitstamp", symbol, None, None, None, fee_pct, withdrawal_fee_usd, str(e))

FETCHERS = {
    "Binance": fetch_binance,
    "Kraken": fetch_kraken,
    "Coinbase": fetch_coinbase,
    "Bybit": fetch_bybit,
    "Bitstamp": fetch_bitstamp,
}


# =========================
# Arbitrage logic
# =========================
def build_quotes(symbol: str, fee_settings: Dict[str, Dict[str, float]], enabled_exchanges: List[str]) -> List[ExchangeQuote]:
    quotes = []
    for exchange in enabled_exchanges:
        config = fee_settings[exchange]
        quote = FETCHERS[exchange](symbol, config["fee_pct"], config["withdrawal_fee_usd"])
        quotes.append(quote)
    return quotes


def quotes_to_df(quotes: List[ExchangeQuote]) -> pd.DataFrame:
    rows = []
    for q in quotes:
        rows.append(
            {
                "Exchange": q.exchange,
                "Symbol": q.symbol,
                "Bid": q.bid,
                "Ask": q.ask,
                "Last": q.last,
                "Trading Fee %": q.fee_pct,
                "Withdrawal Fee (USD)": q.withdrawal_fee_usd,
                "Error": q.error,
            }
        )
    return pd.DataFrame(rows)


def find_arbitrage(quotes: List[ExchangeQuote], capital_usd: float, slippage_pct: float) -> pd.DataFrame:
    opportunities = []
    valid_quotes = [q for q in quotes if q.ask and q.bid]

    for buy_q in valid_quotes:
        for sell_q in valid_quotes:
            if buy_q.exchange == sell_q.exchange:
                continue

            buy_price_effective = buy_q.ask * (1 + buy_q.fee_pct / 100 + slippage_pct / 100)
            sell_price_effective = sell_q.bid * (1 - sell_q.fee_pct / 100 - slippage_pct / 100)

            coin_amount = capital_usd / buy_price_effective if buy_price_effective else 0
            gross_revenue = coin_amount * sell_price_effective
            net_profit = gross_revenue - capital_usd - buy_q.withdrawal_fee_usd - sell_q.withdrawal_fee_usd
            net_profit_pct = (net_profit / capital_usd) * 100 if capital_usd else 0
            spread_pct = ((sell_q.bid - buy_q.ask) / buy_q.ask) * 100 if buy_q.ask else 0

            opportunities.append(
                {
                    "Buy On": buy_q.exchange,
                    "Sell On": sell_q.exchange,
                    "Buy Ask": round(buy_q.ask, 6),
                    "Sell Bid": round(sell_q.bid, 6),
                    "Raw Spread %": round(spread_pct, 4),
                    "Effective Buy Price": round(buy_price_effective, 6),
                    "Effective Sell Price": round(sell_price_effective, 6),
                    "Estimated Coin Amount": round(coin_amount, 8),
                    "Estimated Net Profit (USD)": round(net_profit, 2),
                    "Estimated Net Profit %": round(net_profit_pct, 4),
                }
            )

    df = pd.DataFrame(opportunities)
    if not df.empty:
        df = df.sort_values(by="Estimated Net Profit (USD)", ascending=False).reset_index(drop=True)
    return df


# =========================
# UI
# =========================
st.title("Crypto Arbitrage Scanner")
st.caption("Educational scanner for comparing cross-exchange spreads after fees and slippage.")

with st.sidebar:
    st.header("Settings")
    symbol = st.selectbox("Trading Pair", SYMBOL_OPTIONS, index=0)
    capital_usd = st.number_input("Capital (USD)", min_value=100.0, value=10000.0, step=100.0)
    slippage_pct = st.number_input("Estimated Slippage %", min_value=0.0, value=0.10, step=0.01)
    auto_refresh = st.toggle("Auto Refresh", value=False)
    refresh_seconds = st.slider("Refresh Every (seconds)", min_value=5, max_value=60, value=REFRESH_SECONDS_DEFAULT)

    st.subheader("Enable Exchanges")
    enabled_exchanges = []
    for ex in FETCHERS.keys():
        if st.checkbox(ex, value=True):
            enabled_exchanges.append(ex)

    st.subheader("Fees")
    fee_settings = {}
    for ex in FETCHERS.keys():
        st.markdown(f"**{ex}**")
        fee_pct = st.number_input(f"{ex} trading fee %", min_value=0.0, value=0.10, step=0.01, key=f"fee_{ex}")
        withdrawal_fee_usd = st.number_input(
            f"{ex} withdrawal/network fee (USD)", min_value=0.0, value=5.0, step=0.5, key=f"wd_{ex}"
        )
        fee_settings[ex] = {
            "fee_pct": fee_pct,
            "withdrawal_fee_usd": withdrawal_fee_usd,
        }

refresh_clicked = st.button("Scan Now", type="primary")

if refresh_clicked or auto_refresh:
    if len(enabled_exchanges) < 2:
        st.warning("Enable at least 2 exchanges to evaluate arbitrage.")
    else:
        quotes = build_quotes(symbol, fee_settings, enabled_exchanges)
        quotes_df = quotes_to_df(quotes)
        arb_df = find_arbitrage(quotes, capital_usd, slippage_pct)

        good_quotes = quotes_df[quotes_df["Error"].isna() | (quotes_df["Error"] == None)]
        bad_quotes = quotes_df[quotes_df["Error"].notna()]

        col1, col2 = st.columns([1, 1])
        with col1:
            st.subheader("Live Quotes")
            st.dataframe(quotes_df, use_container_width=True)
        with col2:
            st.subheader("Best Opportunities")
            if arb_df.empty:
                st.info("No arbitrage opportunities found with current assumptions.")
            else:
                st.dataframe(arb_df, use_container_width=True)
                best = arb_df.iloc[0]
                if best["Estimated Net Profit (USD)"] > 0:
                    st.success(
                        f"Best route: Buy on {best['Buy On']} and sell on {best['Sell On']} | "
                        f"Estimated net profit: ${best['Estimated Net Profit (USD)']:.2f}"
                    )
                else:
                    st.warning("Top spread is still not profitable after fees/slippage.")

        if not bad_quotes.empty:
            st.subheader("Endpoint Errors")
            st.dataframe(bad_quotes[["Exchange", "Error"]], use_container_width=True)

        csv_data = arb_df.to_csv(index=False).encode("utf-8") if not arb_df.empty else b""
        st.download_button(
            label="Download Opportunities CSV",
            data=csv_data,
            file_name="arbitrage_opportunities.csv",
            mime="text/csv",
            disabled=arb_df.empty,
        )

        st.markdown("---")
        st.subheader("Notes")
        st.write(
            "This app uses public quote endpoints and estimates simple cross-exchange arbitrage. "
            "Real execution may differ due to latency, order book depth, transfer times, price movement, "
            "regional restrictions, withdrawal holds, and dynamic fees."
        )

    if auto_refresh:
        time.sleep(refresh_seconds)
        st.rerun()
else:
    st.info("Choose settings in the sidebar, then click **Scan Now**.")


# =========================
# Future upgrades
# =========================
# 1. Replace public endpoints with authenticated APIs and deeper order book data.
# 2. Add triangular arbitrage inside one exchange.
# 3. Add websocket streaming for lower latency.
# 4. Track historical spreads and plot profitability over time.
# 5. Add exchange-specific transfer/network selection logic.
