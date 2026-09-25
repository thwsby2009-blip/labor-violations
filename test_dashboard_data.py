import csv
import tempfile
import unittest
from datetime import date
from pathlib import Path

from dashboard_data import articles, load_cases, parse_date


class DataTests(unittest.TestCase):
    def test_dates_and_article_variants(self):
        self.assertEqual(parse_date('115/09/15'), date(2026, 9, 15))
        self.assertEqual(parse_date('2025-01-02'), date(2025, 1, 2))
        self.assertIsNone(parse_date('115/02/30'))
        self.assertEqual(articles('勞基法第30條第1項;第30條第6項;第30條之1'), ['第30-1條', '第30條'])

    def test_duplicates_missing_amounts_and_late_announcements(self):
        rows = [
            ['編號', '縣市／單位別', '公告日期'],
            ['台中市', '115/09/01', '甲', '113/05/01', '中字1', '第24條', '說明', '20,000', ''],
            ['臺中市', '115/09/02', '甲', '113/05/01', '中字1', '第30條', '說明', '20,000', '補登'],
            ['基隆市', '115/09/02', '乙', '114/05/01', '基字1', '第24條', '', '', ''],
            ['1', '台北市', '115/09/02', '丙', '115/05/01', '北字1', '第24條', '', '10000', ''],
            ['台北市', '115/09/02', '丙', '115/05/01', '北字1', '第24條', '', '30000', '更正'],
            ['台北市', '', '丁', '', '', '第24條', '', '', ''],
            ['台北市', '', '戊', '', '', '第24條', '', '', ''],
        ]
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'cases.csv'
            with path.open('w', encoding='utf-8-sig', newline='') as f:
                csv.writer(f).writerows(rows)
            cases, info = load_cases(path)
        self.assertEqual(len(cases), 5)
        self.assertEqual(info['合併列數'], 2)
        self.assertEqual(cases[0]['處分年度'], 2024)
        self.assertEqual(cases[0]['罰鍰金額'], 20000)
        self.assertEqual(cases[0]['公告日期'], date(2026, 9, 2))
        self.assertEqual(cases[0]['條款'], ['第24條', '第30條'])
        self.assertIsNone(cases[1]['罰鍰金額'])
        self.assertEqual(cases[2]['金額狀態'], '金額不一致，未計入')
        self.assertIsNone(cases[2]['罰鍰金額'])


if __name__ == '__main__':
    unittest.main()
