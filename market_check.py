import yfinance as yf


def get_current_quote(ticker: str) -> tuple[float, str]:
    """Fetch last price and currency for ``ticker`` via yfinance ``fast_info``."""
    symbol = ticker.strip().upper()
    stock = yf.Ticker(symbol)
    fast = stock.fast_info
    price = fast["last_price"]
    currency = fast["currency"]
    return float(price), str(currency)


if __name__ == "__main__":
    ticker = "NVDA"
    print(f"Connecting to global markets to fetch {ticker}...")

    try:
        price, currency = get_current_quote(ticker)
        print("\n" + "=" * 30)
        print(f"   {ticker} REAL-TIME DATA")
        print("=" * 30)
        print(f"  PRICE:    {price:.2f} {currency}")
        print(f"  STATUS:   Connected & Live")
        print("=" * 30)
    except Exception as e:
        print(f"Error: {e}")
