from datetime import datetime

import wx
from time import sleep
import pandas as pd

from lightweight_charts import Chart, WxChart


def on_click(x):
    print('yeayea')
    print(x)


class Frame(wx.Frame):
    def __init__(self):
        super().__init__(None)
        self.SetSize(1000, 500)
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        panel.SetSizer(sizer)


        # intervals = ('1 min', '5 min', '30 min', 'H', 'D')
        # switchers = []
        # interval_sizer = wx.BoxSizer(wx.HORIZONTAL)
        # for interval in intervals:
        #     button = wx.Button(panel, label=interval, size=(52, -1))
        #     interval_sizer.Add(button, 0, wx.ALIGN_CENTER | wx.ALL, 3)
        #     switchers.append(button)



        self.chart = WxChart(panel)

        webview = self.chart.get_webview()

        # sizer.Add(interval_sizer, 0, wx.ALIGN_LEFT | wx.ALL)
        sizer.Add(webview, 1, wx.EXPAND | wx.ALL)
        sizer.Layout()
        self.Show()


def start_wx_app():
    app = wx.App()
    frame = Frame()

    df = pd.read_csv('../examples/1_setting_data/ohlcv.csv')
    frame.chart.set(df)
    app.MainLoop()


if __name__ == '__main__':


    start_wx_app()

    chart = Chart(width=1000, debug=True)

    df = pd.read_csv('../examples/1_setting_data/ohlcv.csv')

    chart.set(df)
    chart.legend(True)
    chart.subscribe_click(on_click)

    marker = chart.marker(datetime(year=2023, month=2, day=17))

    line = chart.create_line()

    chart = Chart()

    chart.show(block=True)



