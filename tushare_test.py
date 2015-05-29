# -*- coding: utf-8 -*-
from __future__ import unicode_literals

__author__ = 'huang'


import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import tushare as ts
from matplotlib.ticker import MultipleLocator
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle


def candlestick(ax, data, width=0.6, colorup='r', colordown='g', time_format="%Y-%m-%d", alpha=0.7):
    """ Optimized candle stick graph interface.

        :type ax matplotlib.axes.Axes
    """
    offset = width / 2.0
    timeseries = data.index
    t = [tt.strftime(time_format) for tt in timeseries]
    oo = data['open']
    cc = data['close']
    hh = data['high']
    ll = data['low']

    ax.set_xlim(0.0, len(t)*width)

    major_locator = MultipleLocator(20*width)
    minor_locator = MultipleLocator(5*width)

    ax.set_xticks([x*width for x in range(len(t))], minor=True)

    ticklabels = [t[d] for d in range(len(timeseries)) if d % 20 == 0]
    ticklabels.insert(0, 'dummy')  # fix matplotlib tick bug
    ax.tick_params(axis='both', direction='out', width=2, length=8,
                   labelsize=10, pad=8)
    ax.xaxis.set_ticklabels(ticklabels, horizontalalignment='center')
    ax.xaxis.set_major_locator(major_locator)
    ax.xaxis.set_minor_locator(minor_locator)

    lines = []
    patches = []
    for q in range(len(t)):
        c = float(cc[q])
        o = float(oo[q])
        h = float(hh[q])
        l = float(ll[q])
        if c >= o:
            color = colorup
            lower = o
            height = c - o
        else:
            color = colordown
            lower = c
            height = o - c

        vline = Line2D(
            xdata=(q*width, q*width), ydata=(l, h),
            color=color,
            linewidth=0.5,
            antialiased=True,
        )

        rect = Rectangle(
            xy=(q*width-offset, lower),
            width = width,
            height = height,
            facecolor = color,
            edgecolor = color,
        )
        rect.set_alpha(alpha)

        lines.append(vline)
        patches.append(rect)
        ax.add_line(vline)
        ax.add_patch(rect)

    ax.autoscale_view()
    return lines, patches


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
        fig, ax = plt.subplots()

        candlestick(ax, self._data)

        fig.show()
        return fig, ax

    def candlestick_with_ma(self, ma_params=(5, 10, 20, 30, 60)):
        fig, ax = self.candlestick()
        close_p = self._data['close']
        for para in ma_params:
            ma_s = pd.rolling_mean(close_p, para)
            # switch scalex to False to prevent breaking the x axis tick
            ax.plot([x*0.6 for x in range(len(close_p))], ma_s.values.tolist(),
                    color=np.random.random(3).tolist(),
                    linestyle='-',
                    label='MA'+str(para),
                    linewidth=1.5,
                    scalex=False)

        ax.legend(loc='best')
        return fig, ax

    def candlestick_with_macd(self, macd_params=(12, 26, 9)):
        """ Draw candle stick graph with macd graph"""
        close_p = self._data['close']

        left, width = 0.1, 0.8
        fig = plt.figure(facecolor='white')
        main_rect = [left, 0.4, width, 0.5]
        macd_rect = [left, 0.1, width, 0.3]

        axescolor = '#f6f6f6'

        main_g = fig.add_axes(main_rect, axis_bgcolor=axescolor)
        macd_g = fig.add_axes(macd_rect, axis_bgcolor=axescolor, sharex=main_g)

        candlestick(main_g, self._data)

        # Draw macd graph
        fast_para, slow_para, smooth_para = macd_params
        fast = pd.ewma(close_p, span=fast_para)
        slow = pd.ewma(close_p, span=slow_para)
        diff = fast - slow
        dea = pd.ewma(diff, smooth_para)
        macd = diff - dea

        macd_g.plot([x*0.6 for x in range(len(close_p))],
                    diff.values.tolist(),
                    color='black',
                    linestyle='-',
                    label='DIF',
                    linewidth=1.0,
                    scalex=False)
        macd_g.plot([x*0.6 for x in range(len(close_p))],
                    dea.values.tolist(),
                    color='blue',
                    linestyle='-',
                    label='DEA',
                    linewidth=1.0,
                    scalex=False)
        fillcolor = 'darkslategrey'
        macd_g.fill_between([x*0.6 for x in range(len(close_p))],
                            macd, 0, alpha=0.5,
                            facecolor=fillcolor,
                            edgecolor=fillcolor
                            )

        macd_g.legend(loc='best')
        macd_g.autoscale_view(scalex=False)

        fig.show()
        return fig, main_g, macd_g


if __name__ == '__main__':
    df = ts.get_h_data('601166', start='2014-09-01', end='2015-05-28')
    price_data = PriceData(df)
    price_data.candlestick_with_macd()
