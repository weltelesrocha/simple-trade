import sys

class SimpleTradeBeep:
    def success(self):
        sys.stdout.write('\a')
        sys.stdout.flush()