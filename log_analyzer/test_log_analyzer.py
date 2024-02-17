import unittest
from log_analyzer import log_parser, calculate_statistics


class TestLogParser(unittest.TestCase):
    def test_log_parser_valid_line(self):
        """Testing parsing for valid line"""

        log_line = '1.196.116.32 - - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/banner/25019354 HTTP/1.1" 200 927' \
                   ' "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-"' \
                   ' "1498697422-2190034393-4708-9752759" "dc7161be3" 0.390'
        expected_result = ('/api/v2/banner/25019354', 0.390)
        self.assertEqual(log_parser(log_line), expected_result)

    def test_log_parser_invalid_line(self):
        """Testing for parsing invalid line"""

        log_line = "Hello Word"
        self.assertIsNone(log_parser(log_line))

    def test_log_parser_empty_line(self):
        """Testing for parsing empty line"""

        log_line = ""
        self.assertIsNone(log_parser(log_line))

    def test_log_parser_missing_url(self):
        """Testing for parsing line with missing URL"""

        log_line = '1.196.116.32 - - [29/Jun/2017:03:50:22 +0300] "GET HTTP/1.1" 200 927'
        self.assertIsNone(log_parser(log_line))


class TestCalculateStatistics(unittest.TestCase):
    def setUp(self):
        """Setting up data for testing."""
        self.url_data = {
            '/api/1': [0.2, 0.4, 0.6],
            '/api/2': [0.1, 0.2, 0.3, 0.4]
        }
        self.total_time = sum([sum(times) for times in self.url_data.values()])
        self.total_count = sum([len(times) for times in self.url_data.values()])

    def test_calculate_statistics_correctness(self):
        """Testing correctness of statistics calculation."""
        expected_statistics = {
            '/api/1': {
                'count': 3,
                'count_perc': (3 / self.total_count) * 100,
                'time_sum': sum(self.url_data['/api/1']),
                'time_perc': (sum(self.url_data['/api/1']) / self.total_time) * 100,
                'time_avg': sum(self.url_data['/api/1']) / 3,
                'time_max': max(self.url_data['/api/1']),
                'time_med': sorted(self.url_data['/api/1'])[len(self.url_data['/api/1']) // 2]
            },
            '/api/2': {
                'count': 4,
                'count_perc': (4 / self.total_count) * 100,
                'time_sum': sum(self.url_data['/api/2']),
                'time_perc': (sum(self.url_data['/api/2']) / self.total_time) * 100,
                'time_avg': sum(self.url_data['/api/2']) / 4,
                'time_max': max(self.url_data['/api/2']),
                'time_med': sorted(self.url_data['/api/2'])[len(self.url_data['/api/2']) // 2]
            }
        }

        calculated_statistics = calculate_statistics(self.url_data)
        for url in expected_statistics:
            with self.subTest(url=url):
                self.assertAlmostEqual(calculated_statistics[url]['count_perc'], expected_statistics[url]['count_perc'], places=2)
                self.assertAlmostEqual(calculated_statistics[url]['time_perc'], expected_statistics[url]['time_perc'], places=2)
                self.assertAlmostEqual(calculated_statistics[url]['time_avg'], expected_statistics[url]['time_avg'], places=2)
                self.assertEqual(calculated_statistics[url]['time_max'], expected_statistics[url]['time_max'])
                self.assertEqual(calculated_statistics[url]['time_med'], expected_statistics[url]['time_med'])


if __name__ == '__main__':
    unittest.main()
