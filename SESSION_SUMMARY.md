# VTTHX Portfolio App Development Summary

October 7, 2026

## Project overview

Built a Streamlit app for user-selected mutual funds, defaulting to Vanguard Target Retirement 2035 Fund (VTTHX) with three pages: historical performance, S&P 500 comparison, and a personalized investment projection through December 31, 2035. A searchable ticker box offers common fund suggestions and accepts custom tickers; a dropdown recalls the five most recent unique entries for the current browser session. Features include growth charts, cumulative return, compound annual growth rate (CAGR), volatility, drawdown, calendar-year returns, and CSV downloads. Users can enter a purchase amount/date, monthly contributions, custom return assumptions, and inflation. The UI follows the active light or dark theme. Local address: http://localhost:8501. Public source repository: https://github.com/dougwalkerextension-sketch/stock-performance.

## Datasets used

Yahoo Finance daily history, retrieved through yfinance, supplies adjusted closing prices for **the selected fund (default VTTHX)** and **SPY**, plus the **^GSPC** S&P 500 price index. Downloads request full available history; coverage depends on the selected ticker. A live VFIAX check returned 6,511 observations from November 13, 2000 through October 6, 2026. Adjusted prices approximate reinvested distributions. SPY is the default S&P 500 total-return proxy; ^GSPC excludes dividends. Comparisons use matching observation dates without filling missing prices. Data is cached for one hour and can be refreshed.

The [Vanguard fund fact sheet](https://workplace.vanguard.com/assets/corp/fund_communications/pdf_publish/us-products/fact-sheet/F0305.pdf) supplied fund context, including its increasingly conservative allocation; it was not a historical price dataset. Automated UI tests used synthetic price fixtures, which are never substituted into the running app.

## Prompts used during vibe coding

The user prompts drove implementation directly; no separate generated coding prompts or delegated agent prompts were used.

- **Initial request:** “keep a record of all of this development session and provide a one page summary afterwards. Create a stock portfolio analysis app. It should analyze the performance of the vanguard target retirement fund 2035 VTTHX. Create a streamlit UI that shows historical performance, comparison vs the S&P 500, and a personalized page that allows a user to enter an amount to purchase and show the projected amount at 2035 given past performance.”
- **UI refinement:** “Make the UI work if the user has dark mode active in the browser”
- **Publication:** "publish this to github"; repository visibility: "Public repository".
- **Autocomplete refinement:** "make the box where the user can enter their own funds as an autocomplete. Also have a drop down there that will shown the last five entries"
- **Fund selection refinement:** "Add in the ability for the user to enter the code for any mutual fund, but default to the current one."
- **Summary refinement:** “make sure the summary includes the following Include: project overview, datasets used, prompts you used during vibe coding, iterations you tried, and any learnings or observations from the workflow.”

## Iterations tried

1. Created the three-page app and separate calculation module in an empty workspace. Installed Python 3.12 and dependencies with uv after finding no usable Python interpreter.
2. Validated financial calculations and added Streamlit page checks. Fixed a test-harness failure by resolving the app path relative to the project rather than the tests folder.
3. Replaced deprecated Streamlit layout arguments. Seven tests passed, live data was retrieved for all three tickers, and the local server health check returned ok.
4. Replaced fixed light colors with active-theme CSS variables and enabled Streamlit theming for charts. Tests passed after the theme changes; browser appearance was not manually inspected.

5. Added a normalized ticker input, cached downloads per fund, and dynamic labels and exports across all pages. Nine tests passed, including fund switching and invalid/unavailable ticker handling; live VFIAX data loaded successfully.

6. Added native searchable suggestions, custom ticker entry, and a five-entry recent-funds dropdown. Preserved custom values in suggestions after a test serialization issue. All ten tests passed, including history ordering, deduplication, eviction, and recent-fund selection.

7. Published the reviewed source, tests, README, and session records to the public [stock-performance repository](https://github.com/dougwalkerextension-sketch/stock-performance) on the main branch. Excluded environment files, caches, and server logs.

## Learnings and workflow observations

Benchmark definitions matter: adjusted SPY returns and the dividend-excluding index answer different questions. Matching dates prevents misleading comparisons. Separating calculations from the UI made compounding, drawdowns, and month-end contributions easier to verify. Synthetic fixtures made UI checks independent of provider availability, while a separate live check verified connectivity. Theme-aware colors avoid conflicts between browser preference and custom styling. Cache keys and labels must follow the selected ticker to prevent stale results. Widget callbacks keep autocomplete and recent selections synchronized without changing the fund during unrelated page interactions.

Historical CAGR supports a hypothetical constant-growth illustration, not a guaranteed forecast. VTTHX's changing allocation limits extrapolation; taxes, transaction costs, and future fee changes are excluded. Detailed activity and validation records remain in DEVELOPMENT_LOG.md; restart instructions are in README.md.
