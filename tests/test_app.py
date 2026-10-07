"""UI integration checks with explicitly synthetic fixtures; never served by the app."""
import unittest
from unittest.mock import patch
from pathlib import Path
import numpy as np
import pandas as pd
from streamlit.testing.v1 import AppTest


def fixture():
    dates = pd.bdate_range('2003-10-27', '2026-10-07')
    raw = pd.DataFrame({('Close', 'VTTHX'): 100 * np.exp(np.arange(len(dates)) * .0002), ('Close', 'SPY'): 100 * np.exp(np.arange(len(dates)) * .0003), ('Close', '^GSPC'): 100 * np.exp(np.arange(len(dates)) * .00025)}, index=dates)
    return raw


def set_ticker(app, value):
    widget = app.sidebar.selectbox[0]
    if value is not None and value not in widget.options:
        widget.options.append(value)
    widget.set_value(value).run()


class Pages(unittest.TestCase):
    def test_pages_and_personal_inputs(self):
        with patch('yfinance.download', return_value=fixture()):
            app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py'), default_timeout=30).run()
            self.assertFalse(app.exception)
            self.assertEqual(len(app.metric), 4)
            app.sidebar.radio[0].set_value('S&P 500 comparison').run()
            self.assertFalse(app.exception)
            self.assertGreater(len(app.dataframe), 0)
            app.sidebar.selectbox[3].set_value('^GSPC').run()
            self.assertFalse(app.exception)
            app.sidebar.radio[0].set_value('My 2035 projection').run()
            self.assertFalse(app.exception)
            self.assertEqual(len(app.metric), 3)
            app.number_input[0].set_value(25000).run()
            self.assertFalse(app.exception)
            self.assertEqual(app.metric[1].value, '$25,000')
            app.checkbox[0].set_value(False).run()
            app.number_input[2].set_value(0.0).run()
            self.assertEqual(app.metric[0].value, '$25,000')

    def test_selected_fund_across_pages_and_cache(self):
        from streamlit.runtime.caching import cache_data
        cache_data.clear()
        def prices_for(tickers, **kwargs):
            data = fixture()
            if 'VFIAX' in tickers:
                data[('Close', 'VFIAX')] = data[('Close', 'VTTHX')] ** 1.5
            return data
        with patch('yfinance.download', side_effect=prices_for) as download:
            app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py'), default_timeout=30).run()
            self.assertEqual(app.sidebar.selectbox[0].value, 'VTTHX')
            old_return = app.metric[1].value
            set_ticker(app, '  vfiax  ')
            self.assertFalse(app.exception)
            self.assertNotEqual(app.metric[1].value, old_return)
            self.assertIn('VFIAX', download.call_args.args[0])
            self.assertTrue(any('VFIAX history used' in c.value for c in app.caption))
            app.sidebar.radio[0].set_value('S&P 500 comparison').run()
            self.assertFalse(app.exception)
            self.assertIn('VFIAX', app.dataframe[0].value.columns)
            app.sidebar.radio[0].set_value('My 2035 projection').run()
            self.assertFalse(app.exception)
            self.assertEqual(app.checkbox[0].label, 'Use historical VFIAX CAGR')
            self.assertEqual(len(app.metric), 3)
            set_ticker(app, 'VTTHX')
            self.assertFalse(app.exception)
            self.assertEqual(app.checkbox[0].label, 'Use historical VTTHX CAGR')
            self.assertEqual(download.call_count, 2)
        cache_data.clear()

    def test_invalid_and_unavailable_tickers(self):
        from streamlit.runtime.caching import cache_data
        cache_data.clear()
        with patch('yfinance.download', return_value=fixture()) as download:
            app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py'), default_timeout=30).run()
            set_ticker(app, ' ')
            self.assertFalse(app.exception)
            self.assertTrue(app.error)
            self.assertEqual(download.call_count, 1)
            set_ticker(app, 'VTTHX,SPY')
            self.assertTrue(app.error)
            self.assertEqual(download.call_count, 1)
            set_ticker(app, 'MISSING')
            self.assertFalse(app.exception)
            self.assertIn('MISSING', app.error[0].value)
            self.assertEqual(len(app.metric), 0)
        cache_data.clear()

    def test_autocomplete_and_five_recent_funds(self):
        from streamlit.runtime.caching import cache_data
        cache_data.clear()
        def prices_for(tickers, **kwargs):
            data = fixture()
            for ticker in tickers:
                if ('Close', ticker) not in data.columns:
                    data[('Close', ticker)] = data[('Close', 'VTTHX')]
            return data
        with patch('yfinance.download', side_effect=prices_for):
            app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py'), default_timeout=30).run()
            self.assertTrue(app.sidebar.selectbox[0].proto.accept_new_options)
            self.assertIn('VFIAX', app.sidebar.selectbox[0].options)
            for ticker in ['VFIAX', 'VTSAX', 'VBTLX', 'FXAIX', 'SWPPX', 'CUSTOMX']:
                set_ticker(app, ticker)
                self.assertFalse(app.exception)
            self.assertEqual(app.session_state['recent_funds'], ['CUSTOMX', 'SWPPX', 'FXAIX', 'VBTLX', 'VTSAX'])
            app.sidebar.selectbox[1].set_value('VBTLX').run()
            self.assertFalse(app.exception)
            self.assertEqual(app.sidebar.selectbox[0].value, 'VBTLX')
            self.assertEqual(app.session_state['recent_funds'], ['VBTLX', 'CUSTOMX', 'SWPPX', 'FXAIX', 'VTSAX'])
            self.assertIsNone(app.sidebar.selectbox[1].value)
            app.sidebar.radio[0].set_value('My 2035 projection').run()
            self.assertEqual(app.checkbox[0].label, 'Use historical VBTLX CAGR')
            self.assertEqual(app.session_state['recent_funds'][0], 'VBTLX')
            set_ticker(app, 'VBTLX')
            self.assertEqual(len(app.session_state['recent_funds']), 5)
        cache_data.clear()

    def test_failed_data_shows_error(self):
        from streamlit.runtime.caching import cache_data
        cache_data.clear()
        with patch('yfinance.download', return_value=pd.DataFrame()):
            app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py'), default_timeout=30).run()
            self.assertFalse(app.exception)
            self.assertGreater(len(app.error), 0)
        cache_data.clear()

if __name__ == '__main__':
    unittest.main()

