import pandas as pd
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from lightweight_charts.widgets import QtChart

app = QApplication([])
window = QMainWindow()
window.resize(800, 500)
layout = QVBoxLayout()
layout.setContentsMargins(0, 0, 0, 0)
widget = QWidget()
widget.setLayout(layout)

chart = QtChart(widget)

df = pd.read_csv('../examples/1_setting_data/ohlcv.csv')
chart.set(df)

layout.addWidget(chart.get_webview())

window.setCentralWidget(widget)
window.show()

app.exec_()
