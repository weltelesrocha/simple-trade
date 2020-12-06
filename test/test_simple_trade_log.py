from library import SimpleTradeLog
import unittest


class TestSimpleTradeLog(unittest.TestCase):
    def test_info(self):
        log = SimpleTradeLog(SimpleTradeLog.LEVEL_INFO)
        log.info('Hello World!')


if __name__ == '__main__':
    unittest.main()
