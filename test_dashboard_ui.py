"""Exercise real-data chart rendering, filters, and empty states."""
import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


class DashboardTests(unittest.TestCase):
    def test_filters_and_empty_results(self):
        app = AppTest.from_file(str(Path(__file__).parent / 'app.py'), default_timeout=60).run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.get('vega_lite_chart')), 3)
        self.assertGreater(int(app.metric[0].value.replace(',', '')), 70000)
        app.selectbox[0].select('2025')
        app.selectbox[1].select('臺中市')
        app.selectbox[2].select('第24條')
        app.run()
        self.assertFalse(app.exception)
        details = app.dataframe[-1].value
        self.assertTrue((details['單位'] == '臺中市').all())
        self.assertTrue(details['處分日期'].str.startswith('2025/').all())
        self.assertGreater(len(details), 0)
        app.text_input[0].input('__NO_COMPANY_MATCH_95253__').run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value, '0')
        self.assertEqual(len(app.get('vega_lite_chart')), 0)
        app.text_input[0].input('')
        app.selectbox[0].select('全部年度')
        app.selectbox[1].select('全部')
        app.selectbox[2].select('全部')
        app.run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.get('vega_lite_chart')), 3)


if __name__ == '__main__':
    unittest.main()
