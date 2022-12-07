# The Tick Candle Class
class StockCandle:
    def __init__(self, transactions):
        self.is_reversal = False
        self.start_price = transactions[-1].get_price()
        self.end_price = transactions[0].get_price()
        self.difference = float(self.end_price) - float(self.start_price)
        self._calc_highest(transactions)
        self._calc_lowest(transactions)

    def _calc_highest(self, txs):
        self.highest_price = max(map(lambda tx: tx.get_price(), txs))

    def _calc_lowest(self, txs):
        self.lowest_price = min(map(lambda tx: tx.get_price(), txs))
