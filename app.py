from datetime import date
from zoneinfo import ZoneInfo
from datetime import datetime

import re

import pandas as pd
import plotly.express as px
import streamlit as st
import yfinance as yf

from analysis import metrics, project

st.set_page_config(page_title="2035 Portfolio Studio", page_icon="📈", layout="wide")
st.markdown("""<style>
.stApp {background: var(--background-color); color: var(--text-color);}
[data-testid="stMetric"] {background:var(--secondary-background-color);color:var(--text-color);padding:18px;border-radius:12px;border:1px solid var(--text-color);border-color:color-mix(in srgb, var(--text-color) 18%, transparent);}
</style>""", unsafe_allow_html=True)
TODAY = datetime.now(ZoneInfo("America/Los_Angeles")).date()
TARGET = date(2035, 12, 31)
LABELS = {"VTTHX": "VTTHX", "SPY": "S&P 500 proxy (SPY)", "^GSPC": "S&P 500 price index"}

@st.cache_data(ttl=3600, show_spinner=False)
def load_prices(ticker):
    raw = yf.download(list(dict.fromkeys([ticker, "SPY", "^GSPC"])), period="max", auto_adjust=True,
                      progress=False, threads=False, timeout=25)
    if raw is None or raw.empty:
        raise ValueError("Yahoo Finance returned no historical prices.")
    prices = raw["Close"].copy()
    prices.index = pd.to_datetime(prices.index).tz_localize(None)
    return prices.sort_index().where(lambda x: x > 0)

st.sidebar.title("2035 Portfolio Studio")
FUND_SUGGESTIONS = ["VTTHX", "VFIAX", "VTSAX", "VBTLX", "VTIAX", "VIGAX",
                    "VSMAX", "VIMAX", "VTMGX", "VTIVX", "VFORX", "VTHRX",
                    "VFFVX", "VFIFX", "VTTWX", "VTXVX", "VTTVX", "FXAIX",
                    "FSKAX", "FZROX", "FZILX", "SWPPX", "SWTSX"]
st.session_state.setdefault("fund_ticker", "VTTHX")
st.session_state.setdefault("recent_funds", ["VTTHX"])


def remember_fund(value):
    normalized = (value or "").strip().upper()
    if re.fullmatch(r"[A-Z0-9][A-Z0-9.^-]{0,19}", normalized):
        st.session_state.recent_funds = [normalized] + [
            item for item in st.session_state.recent_funds if item != normalized
        ][:4]
    return normalized


def fund_changed():
    st.session_state.fund_ticker = remember_fund(st.session_state.fund_ticker)


def recent_fund_selected():
    selected = st.session_state.recent_fund_picker
    if selected:
        st.session_state.fund_ticker = remember_fund(selected)
    st.session_state.recent_fund_picker = None


suggestions = list(dict.fromkeys(FUND_SUGGESTIONS + st.session_state.recent_funds +
                                [st.session_state.fund_ticker]))
ticker_input = st.sidebar.selectbox(
    "Mutual fund ticker", suggestions, key="fund_ticker",
    accept_new_options=True, on_change=fund_changed,
    placeholder="Search suggestions or enter a ticker",
    help="Type to filter common fund suggestions, or enter another Yahoo Finance ticker and press Enter.",
)
ticker = (ticker_input or "").strip().upper()
st.sidebar.selectbox(
    "Recent funds (last five)", st.session_state.recent_funds,
    index=None, key="recent_fund_picker", on_change=recent_fund_selected,
    placeholder="Choose a recent fund",
    help="Five unique entries, newest first. History lasts for this browser session.",
)
st.sidebar.caption("Vanguard Target Retirement 2035 | VTTHX" if ticker == "VTTHX" else f"Selected fund: {ticker}")
page = st.sidebar.radio("Explore", ["Historical performance", "S&P 500 comparison", "My 2035 projection"])
window = st.sidebar.selectbox("Historical lookback", ["5 years", "10 years", "3 years", "1 year", "Since inception"], index=1)
benchmark = st.sidebar.selectbox("S&P 500 benchmark", ["SPY", "^GSPC"], format_func=lambda x: LABELS[x])
if st.sidebar.button("Refresh market data"):
    load_prices.clear()
st.sidebar.caption("Data: Yahoo Finance via yfinance. Cached for one hour. No orders are placed.")

st.title(page)
st.caption(f"Analyze {ticker or 'your fund'}. Explore the road to 2035.")
if not re.fullmatch(r"[A-Z0-9][A-Z0-9.^-]{0,19}", ticker):
    st.error("Enter one valid mutual fund ticker, such as VTTHX or VFIAX.")
    st.stop()
try:
    with st.spinner("Loading historical market data…"):
        all_prices = load_prices(ticker)
    if ticker not in all_prices or all_prices[ticker].dropna().empty:
        raise ValueError(f"No historical data is available for {ticker}. Check the ticker and Yahoo Finance coverage.")
    fund = all_prices[ticker].dropna()
    years = {"1 year": 1, "3 years": 3, "5 years": 5, "10 years": 10}.get(window)
    cutoff = fund.index[-1] - pd.DateOffset(years=years) if years else fund.index[0]
    fund = fund.loc[fund.index >= cutoff]
    if len(fund) < 2:
        raise ValueError("At least two historical observations are required.")
except Exception as exc:
    st.error(f"Market data could not be loaded: {exc}")
    st.info("Check your internet connection and try Refresh market data. Yahoo Finance may temporarily rate-limit requests. No sample prices are substituted.")
    st.stop()

st.caption(f"{ticker} history used: {fund.index[0]:%b %d, %Y} – {fund.index[-1]:%b %d, %Y} · {len(fund):,} observations")
if (pd.Timestamp(TODAY) - fund.index[-1]).days > 7:
    st.warning(f"The latest available {ticker} observation is more than seven days old.")

if page == "Historical performance":
    m = metrics(fund)
    cols = st.columns(4)
    for col, label, value in zip(cols, ["Cumulative return", "Annualized return (CAGR)", "Annualized volatility", "Maximum drawdown"], m):
        col.metric(label, f"{value:.2%}")
    growth = (fund / fund.iloc[0] * 10000).rename(ticker)
    st.plotly_chart(px.line(growth, title="Growth of $10,000 • distributions reinvested", labels={"value":"Portfolio value ($)", "index":"Date"}), theme="streamlit", width="stretch")
    tabs = st.tabs(["Calendar-year returns", "Drawdowns", "Historical data"])
    with tabs[0]:
        year_end = fund.resample("YE").last()
        annual = year_end.pct_change().dropna()
        if not annual.empty:
            frame = pd.DataFrame({"Year": annual.index.year.astype(str), "Return (%)": annual.values * 100})
            st.plotly_chart(px.bar(frame, x="Year", y="Return (%)"), theme="streamlit", width="stretch")
        st.caption("Only years with a prior year-end observation are shown. The last year may be partial.")
    with tabs[1]:
        st.plotly_chart(px.area((fund / fund.cummax() - 1) * 100, labels={"value":"Drawdown (%)", "index":"Date"}), theme="streamlit", width="stretch")
    with tabs[2]:
        st.dataframe(fund.rename("Adjusted close ($)"), width="stretch")
        st.download_button(f"Download {ticker} history", fund.to_csv().encode(), f"{ticker.lower()}_history.csv", "text/csv")

elif page == "S&P 500 comparison":
    if benchmark not in all_prices:
        st.error("Selected benchmark data is unavailable.")
        st.stop()
    common = pd.concat([all_prices[ticker].rename(ticker),
                        all_prices[benchmark].rename(LABELS[benchmark])], axis=1)
    common = common.loc[common.index >= cutoff].dropna()
    if len(common) < 2:
        st.error("There is insufficient overlapping fund and benchmark data.")
        st.stop()
    st.caption(f"Both series use matching dates: {common.index[0]:%b %d, %Y} – {common.index[-1]:%b %d, %Y}.")
    st.plotly_chart(px.line(common / common.iloc[0] * 10000, title="Growth of $10,000 on a shared timeline", labels={"value":"Value ($)", "index":"Date", "variable":"Investment"}), theme="streamlit", width="stretch")
    table = pd.DataFrame({column: metrics(common[column]) for column in common}, index=["Cumulative return", "CAGR", "Annualized volatility", "Maximum drawdown"])
    st.dataframe(table.style.format("{:.2%}"), width="stretch")
    st.info("SPY is an investable S&P 500 ETF proxy; adjusted prices include distributions and reflect ETF expenses. The ^GSPC price index excludes dividends, so that comparison uses different return definitions. The selected fund may have a different asset allocation and risk profile from the S&P 500.")
    st.download_button("Download aligned comparison", common.to_csv().encode(), f"{ticker.lower()}_comparison.csv", "text/csv")

else:
    historical_rate = metrics(fund)[1]
    left, right = st.columns([1, 2])
    with left:
        amount = st.number_input("Amount to purchase ($)", min_value=0.0, value=10000.0, step=1000.0)
        purchase = st.date_input("Purchase date", value=TODAY, min_value=TODAY, max_value=max(TODAY, TARGET))
        monthly = st.number_input("Additional monthly contribution ($)", min_value=0.0, value=0.0, step=100.0)
        use_history = st.checkbox(f"Use historical {ticker} CAGR", value=True)
        custom = st.number_input("Custom annual return (%)", min_value=-99.0, max_value=100.0, value=round(historical_rate * 100, 2), disabled=use_history)
        rate = historical_rate if use_history else custom / 100
        inflation = st.slider("Assumed annual inflation (%)", 0.0, 10.0, 2.5, 0.1) / 100
    if purchase >= TARGET:
        st.warning("Choose a purchase date before December 31, 2035 to calculate future growth.")
    else:
        path = project(amount, monthly, rate, purchase, TARGET)
        terminal = path["Projected value"].iloc[-1]
        invested = path["Contributed"].iloc[-1]
        duration = (TARGET - purchase).days / 365.25
        with right:
            a, b, c = st.columns(3)
            a.metric("Projected value • Dec 31, 2035", f"${terminal:,.0f}")
            b.metric("Total contributed", f"${invested:,.0f}")
            c.metric("In purchase-date dollars", f"${terminal / (1 + inflation) ** duration:,.0f}")
            st.caption(f"Annual return assumption: {rate:.2%} · Horizon: {duration:.2f} years")
            st.plotly_chart(px.line(path, x="Date", y=["Projected value", "Contributed"], labels={"value":"Amount ($)", "variable":""}), theme="streamlit", width="stretch")
        scenarios = []
        for label, scenario_rate in [("Lower growth (−3 percentage points)", max(-0.99, rate - .03)), ("Selected assumption", rate), ("Higher growth (+3 percentage points)", rate + .03)]:
            value = project(amount, monthly, scenario_rate, purchase, TARGET)["Projected value"].iloc[-1]
            scenarios.append({"Scenario":label, "Annual return":f"{scenario_rate:.2%}", "2035 value":f"${value:,.0f}"})
        st.dataframe(pd.DataFrame(scenarios), hide_index=True, width="stretch")
        st.caption("Scenarios are illustrations, not probabilities or confidence intervals.")
        st.download_button("Download my projection", path.to_csv(index=False).encode(), f"{ticker.lower()}_2035_projection.csv", "text/csv")
    st.info("This is a hypothetical constant-growth illustration, not a forecast or guarantee. Past performance does not predict future results. Future returns and asset allocation may differ from the historical period. Taxes, transaction costs, and future fee changes are excluded; historical adjusted prices reflect fund expenses and assume reinvestment. Monthly contributions occur at each monthly anniversary after the purchase date, including the target date if it is an anniversary.")

    if ticker == "VTTHX":
        st.caption("VTTHX becomes more conservative as its target date approaches.")

with st.expander("Data and calculation methodology"):
    st.markdown(f"""Returns use Yahoo Finance adjusted closing prices as a reinvested-distribution approximation. CAGR = (last / first)^(365.25 / elapsed days) − 1. Volatility is the sample standard deviation of daily returns × √252. Maximum drawdown is the worst decline from a previous historical peak. Missing observations are removed, never forward-filled. Lookbacks end at the latest available fund observation. Projection growth uses actual elapsed days / 365.25, with monthly anniversary contributions at period end. A target retirement year is not a maturity date or guaranteed payout.

Sources: [VTTHX reference fact sheet](https://workplace.vanguard.com/assets/corp/fund_communications/pdf_publish/us-products/fact-sheet/F0305.pdf) · [Yahoo Finance {ticker}](https://finance.yahoo.com/quote/{ticker}/history/) · [yfinance documentation](https://ranaroussi.github.io/yfinance/reference/api/yfinance.download.html).""")



