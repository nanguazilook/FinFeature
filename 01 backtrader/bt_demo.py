import backtrader as bt
import tushare as ts
import pandas as pd
from datetime import datetime
pro = ts.pro_api()
def prepare_data(ticker,start_date,end_date):
    df = pro.daily(ts_code=ticker,start_date=start_date,end_date=end_date)
    print(df)
    df = df.sort_values(by=['trade_date'])
    df = df.rename(columns={'trade_date':'datetime'})
    df['datetime'] = pd.to_datetime(df['datetime'])
    cols = list(df.columns)
    col = cols[1:6]
    col.append('vol')
    print(col)
    df = df[col]
    df = df.rename(columns={'vol': 'volume'})
    df.set_index('datetime', inplace=True)
    print(df)
    return df

class DualMovingAverageStrategy(bt.Strategy):
    params = dict(
        period1=5,  # 短期均线周期
        period2=20  # 长期均线周期
    )

    def __init__(self):
        self.sma1 = bt.indicators.SimpleMovingAverage(
            self.data0.close, period=self.params.period1
        )
        self.sma2 = bt.indicators.SimpleMovingAverage(
            self.data0.close, period=self.params.period2
        )
        self.cross = bt.indicators.CrossOver(self.sma1, self.sma2)  # 交叉指标

    def next(self):
        if not self.position:
        # 如果短期均线向上穿过长期均线，则买入
            if self.cross > 0:
                self.buy()
        else:

        # 如果短期均线向下穿过长期均线，则卖出
            if self.cross < 0:
                self.sell()
    def notify_trade(self, trade):
        if trade.isclosed:
            print('Trade Profit, Gross {}, Net {}'.format(
                trade.pnl,
                trade.pnlcomm))


if __name__=='__main__':
    #准备数据

    df = prepare_data('601398.SH','20180222','20230601')
    data = bt.feeds.PandasData(
        dataname=df, fromdate=datetime(2019, 1, 1), todate=datetime(2020, 5, 31))

    cerebro = bt.Cerebro()


    cerebro.adddata(data)

    cerebro.addstrategy(DualMovingAverageStrategy)

    cerebro.addsizer(bt.sizers.PercentSizer, percents=90)

    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='mysharpe')
    cerebro.addanalyzer(bt.analyzers.Returns,_name='myreturn')

    result = cerebro.run()
    print('夏普率：', result[0].analyzers.mysharpe.get_analysis()['sharperatio'])
    print('总回报率：', result[0].analyzers.myreturn.get_analysis()['rtot'])

    cerebro.plot()
