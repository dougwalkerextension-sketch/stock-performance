# VTTHX Portfolio Studio

A Streamlit app with a mutual fund ticker selector defaulting to VTTHX, historical fund performance, an aligned S&P 500 comparison, and a personalized purchase projection through December 31, 2035.

## Run on Windows

Using uv (installs Python if needed):

```powershell
uv venv --python 3.12
uv pip install --python .venv\Scripts\python.exe -r requirements.txt
.venv\Scripts\python.exe -m streamlit run app.py
```

Or create a Python 3.12 virtual environment with `python -m venv .venv`, install requirements with its Python, and run the same Streamlit command. Internet access is required for market data. No API key is needed.

## Run on macOS or Linux

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py
```

## Features and assumptions

- Use the searchable mutual fund ticker box in the sidebar (default VTTHX). Type to filter common fund suggestions or enter a new Yahoo Finance ticker. A separate recent-funds dropdown retains five unique entries, newest first, for the current browser session. History, comparison, projections, and exports follow the selected fund; unavailable tickers show a clear error. Full available history is requested, including funds older than VTTHX.
- Three pages: historical performance, S&P 500 comparison, and personal projection.
- Selectable 1/3/5/10-year or inception history; CAGR, cumulative return, volatility, drawdown, calendar-year chart, and CSV downloads.
- SPY adjusted close is the default total-return proxy; optional ^GSPC excludes dividends and is explicitly labeled.
- Comparison drops missing rows so both assets use the same observation dates.
- Projection accepts a purchase amount/date, monthly contributions, historical or custom return, and inflation; includes illustrative return sensitivity.
- Prices are adjusted for distributions, cached for one hour, and refreshable. Failures produce an actionable error without fabricated fallback data.
- Projections are educational illustrations. Historical returns do not guarantee future returns, especially as VTTHX changes its asset allocation.

## Validation

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Session records: DEVELOPMENT_LOG.md and SESSION_SUMMARY.md.
