# Development session record

Date: October 7, 2026 (America/Los_Angeles).

## Request
Keep a record of this development session, provide a one-page summary, and create a Streamlit stock portfolio analysis app for VTTHX with historical performance, S&P 500 comparison, and personalized purchase projection to 2035.

## Discovery
- Workspace was empty; no existing app or repository instructions were found.
- Python on PATH was an inaccessible Windows Store alias. uv was available, but interpreter discovery found no installed Python.
- Read-only sandbox requires permission for project writes, interpreter installation, and dependency installation.

## Research and decisions
- Consulted Vanguard's VTTHX fact sheet, yfinance download documentation, and Streamlit multipage documentation.
- Vanguard describes VTTHX as a stock/bond retirement fund that becomes more conservative over time.
- Use Yahoo Finance adjusted close for historical reinvestment approximation. Use SPY for the default S&P 500 total-return proxy; offer ^GSPC with dividend exclusion clearly disclosed.
- Align benchmark observations without forward filling; measure lookbacks from the latest available fund date.
- Use elapsed-day CAGR and growth to December 31, 2035, with optional monthly anniversary contributions, custom rates, inflation, and sensitivity scenarios.
- Keep projections educational and show assumptions in the UI.

## Implementation
Created app.py, analysis.py, requirements.txt, README.md, .gitignore, and calculation tests. Three navigable pages include interactive charts, metrics, CSV exports, caching, refresh, and market-data error handling. No order execution or personal-data persistence.

## Validation
Pending environment setup and execution; results will be appended below.

This is a task/activity record, not a verbatim chat transcript or a record of hidden reasoning.

## Final validation and delivery
- Installed managed Python 3.12.15 and a workspace virtual environment with the app dependencies.
- Five calculation tests passed: known CAGR/drawdown, monthly contributions with month-end dates and partial months, exact elapsed-day compounding, negative return/zero purchase, and invalid inputs.
- Added two Streamlit integration tests covering all three pages, both benchmarks, changed purchase amounts, custom zero-growth projections, and the data-unavailable state. An initial relative-path issue in the test harness was corrected.
- All seven tests passed after final layout changes. Integration tests use synthetic fixtures only within tests, not app runtime.
- Live Yahoo Finance check returned 21 VTTHX observations and 22 observations each for SPY and ^GSPC over the last month, ending October 7, 2026.
- Updated deprecated Streamlit layout arguments. A pandas/NumPy resampling deprecation warning remains in the dependency stack; it did not affect results.
- Started Streamlit locally on 127.0.0.1:8501, process ID 10384. Health endpoint returned ok. No public deployment was performed.
- Saved SESSION_SUMMARY.md as the requested one-page development summary.
- UI behavior was checked through Streamlit AppTest; no manual browser visual inspection was performed.

## Dark mode follow-up
- Request: make the UI work when the browser uses dark mode.
- Removed fixed light backgrounds and dark heading colors. App text, backgrounds, metric cards, and borders now use Streamlit's active theme CSS variables, respecting both automatic browser preference and an explicit Streamlit theme selection.
- Explicitly enabled Streamlit's theme for all Plotly charts.
- Existing seven tests passed after the change. Browser visual contrast was not manually inspected.

## Summary coverage follow-up
- Request: include project overview, datasets used, vibe-coding prompts, iterations, and workflow learnings or observations.
- Reorganized SESSION_SUMMARY.md into those five sections, preserving validation results and projection limitations.
- Included the actual user prompts, distinguished live datasets from synthetic test fixtures and Vanguard reference material, and documented the test-path correction and dark-mode iteration.
- Reviewed the saved summary against the session record. No application code changed.


## Mutual fund ticker follow-up
- Request: allow any mutual fund code while defaulting to VTTHX.
- Added a sidebar ticker field with whitespace trimming, uppercase normalization, and single-symbol validation. All pages and export filenames now use the selected ticker.
- Cache entries are keyed by ticker. Downloads request maximum available history instead of a VTTHX-specific start date. Missing fund data shows an error, with no stale-fund fallback.
- Generalized fund descriptions and projection assumptions; the VTTHX allocation note appears only for VTTHX. The projection horizon remains December 31, 2035.
- Nine tests passed, covering selected-fund calculations, both comparison/projection pages, cache separation, returning to VTTHX, and invalid/unavailable symbols.
- Live VFIAX download returned 6,511 observations spanning November 13, 2000 through October 6, 2026. Yahoo Finance coverage limits supported symbols; the input does not independently certify instrument type.
- Updated README.md and the summary's overview, datasets, prompts, iterations, and learnings.


## Autocomplete and recent funds follow-up
- Request: autocomplete for the mutual fund entry box and a dropdown showing the last five entries.
- Replaced text input with Streamlit's searchable selectbox accepting new options. Suggestions come from a common-fund ticker list plus recent/custom entries; no claim of exhaustive live symbol search is made.
- Added a separate recent-funds dropdown storing up to five normalized unique entries, newest first, in per-user Streamlit session state. VTTHX remains the initial default. Repeated entries move to the top, older entries are evicted, and syntactically invalid entries are excluded. Provider-unavailable but syntactically valid entries remain recallable.
- Recent selection updates the main ticker through a callback and resets the recent picker. History persists across page changes within the browser session, not across new sessions or server restarts.
- Updated tests for the selectbox UI. AppTest's custom-option serialization required retaining selected custom values in the option list and a helper to send custom strings. All ten tests passed.
- Updated README and summary with functionality, the user prompt, iteration details, and observations. Browser appearance was not manually inspected.
- Reference: https://docs.streamlit.io/develop/api-reference/widgets/st.selectbox


## GitHub publication
- User requested publication to GitHub and selected public visibility; intended repository name is stock-performance.
- Reviewed tracked files for credentials and excluded .venv, caches, and server logs via .gitignore.
- Installed Git, initialized a main branch, and staged app source, tests, and documentation. Added portable run instructions and line-ending settings.
- Publication result will be recorded after GitHub authentication and push are verified.

- Publication verified: https://github.com/dougwalkerextension-sketch/stock-performance (public), main branch, initial commit 2489ec8.
- GitHub device authentication completed for dougwalkerextension-sketch; configured repository-local author identity using GitHub's noreply address.
- GitHub CLI installation completed after a delay. A portable CLI download was also extracted outside the repository during troubleshooting; it is not included in the published files.
- Pushed ten reviewed files. Updated summary with the repository URL and publication prompt; this follow-up documentation is committed separately.
- GitHub hosts the source repository; the running Streamlit app remains local. Existing ten passing tests remain the latest validation; publication changed documentation only.
