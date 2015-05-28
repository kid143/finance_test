# -*- coding: utf-8 -*-
from __future__ import unicode_literals

__author__ = 'huang'


import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import tushare as ts
from matplotlib.finance import candlestick2_ochl
from datetime import timedelta


class PriceData(object):

    def __init__(self, dataframe):
        """ Tushare returned Pandas DataFrame Proxy with finance plot enhancement.

            :type dataframe pandas.DataFrame
        """
        self._data = dataframe.sort_index(ascending=True)

    def __getattr__(self, item):
        return getattr(self._data, item)

    @property
    def original(self):
        return self._data

    def candlestick(self):
        """ Draw candlestick plot for the asset price.

        :rtype fig matplotlib.figure.Figure
        :rtype ax matplotlib.axes.Axes
        """
        timeseries = self._data.index
        open_p = self._data['open']
        close_p = self._data['close']
        high_p = self._data['high']
        low_p = self._data['low']

        fig, ax = plt.subplots()

        ax.autoscale_view()

        x_len = len(timeseries)
        rest = (x_len - 1) % 20
        last = timeseries[-1]
        last_time = last + timedelta(20 - rest)
        ticklabels = [timeseries[d].strftime('%Y-%m-%d') for d in range(len(timeseries)) if d % 20 == 0]
        if last_time != last:
            ticklabels.append(last_time.strftime('%Y-%m-%d'))
        ax.tick_params(axis='both', direction='out', width=2, length=8,
                       labelsize=len(ticklabels), pad=8)
        ax.set_xticklabels(ticklabels, rotation=45, horizontalalignment='right')

        candlestick2_ochl(ax, open_p, close_p, high_p, low_p, width=0.6, colorup='r', colordown='g')

        fig.show()
        return fig, ax

    def candlestick_with_ma(self, ma_params=(5, 10, 20, 30, 60)):
        fig, ax = self.candlestick()
        close_p = self._data['close']
        for para in ma_params:
            ma_s = pd.rolling_mean(close_p, para)
            # switch scalex to False to prevent breaking the x axis tick
            ax.plot(ma_s.values.tolist(),
                    color=np.random.random(3).tolist(),
                    linestyle='-',
                    label='MA'+str(para),
                    linewidth=1.5,
                    scalex=False)

        ax.legend(loc='best')
        return fig, ax


if __name__ == '__main__':
    df = ts.get_h_data('601166', start='2014-09-01', end='2015-05-28')
    price_data = PriceData(df)
    price_data.candlestick_with_ma()
