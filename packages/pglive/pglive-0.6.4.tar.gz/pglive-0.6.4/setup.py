# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pglive',
 'pglive.examples_pyqt5',
 'pglive.examples_pyqt5.designer_example',
 'pglive.examples_pyqt6',
 'pglive.examples_pyqt6.designer_example',
 'pglive.examples_pyside2',
 'pglive.examples_pyside6',
 'pglive.sources']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.24.2,<2.0.0', 'pyqtgraph>=0.13.3,<0.14.0']

setup_kwargs = {
    'name': 'pglive',
    'version': '0.6.4',
    'description': 'Pyqtgraph live plot',
    'long_description': '# Live pyqtgraph plot\n\nPglive package adds support for thread-safe live plotting to pyqtgraph.  \nIt supports PyQt5, PyQt6, PySide2 and PySide6.\n\n# Description #\n\nBy default, pyqtgraph doesn\'t support live plotting. Aim of this package is to provide easy implementation of Line,\nScatter and Bar Live plot. Every plot is connected with it\'s DataConnector, which sole purpose is to consume data points\nand manage data re-plotting. DataConnector interface provides Pause and Resume method, update rate and maximum number of\nplotted points. Each time data point is collected, call `DataConnector.cb_set_data`\nor `DataConnector.cb_append_data_point` callback. That\'s all You need to update plot with new data. Callbacks are Thread\nsafe, so it works nicely in applications with multiple data collection Threads.\n\n**Focus on data collection and leave plotting to pglive.**\n\nTo make firsts steps easy, package comes with many examples implemented in PyQt5 or PyQt6.\nSupport for PySide2 and PySide6 was added in version 0.3.0.\n\n# Code examples #\n\n```python\nimport sys\nfrom math import sin\nfrom threading import Thread\nfrom time import sleep\n\nfrom PyQt6.QtWidgets import QApplication\n\nfrom pglive.sources.data_connector import DataConnector\nfrom pglive.sources.live_plot import LiveLinePlot\nfrom pglive.sources.live_plot_widget import LivePlotWidget\n\n"""\nLine plot is displayed in this example.\n"""\napp = QApplication(sys.argv)\nrunning = True\n\nplot_widget = LivePlotWidget(title="Line Plot @ 100Hz")\nplot_curve = LiveLinePlot()\nplot_widget.addItem(plot_curve)\n# DataConnector holding 600 points and plots @ 100Hz\ndata_connector = DataConnector(plot_curve, max_points=600, update_rate=100)\n\n\ndef sin_wave_generator(connector):\n    """Sine wave generator"""\n    x = 0\n    while running:\n        x += 1\n        data_point = sin(x * 0.01)\n        # Callback to plot new data point\n        connector.cb_append_data_point(data_point, x)\n\n        sleep(0.01)\n\n\nplot_widget.show()\nThread(target=sin_wave_generator, args=(data_connector,)).start()\napp.exec()\nrunning = False\n```\n\nOutput:\n\n![Plot example](https://i.postimg.cc/RFYGfNS6/pglive.gif)\n\nTo run built-in examples, use python3 -m parameter like:  \n`python3 -m pglive.examples_pyqt6.all_plot_types`  \n`python3 -m pglive.examples_pyqt6.crosshair`\n\n# Using PyQt5/6 designer #\n\n1. Add QWidget to Your layout\n2. Promote QWidget to `LivePlotWidget` and set header file to `pglive.sources.live_plot_widget`\n3. Click `Add` and `Promote` button\n\n![All plot types](https://i.postimg.cc/m25NVJZm/designer-promotion.png)\n\n# Available plot types #\n\nPglive supports four plot types: `LiveLinePlot`, `LiveScatterPlot`, `LiveHBarPlot` (horizontal bar plot),\n`LiveVBarPlot` (vertical bar plot) and `LiveCandleStickPlot`.\n\n![All plot types](https://i.postimg.cc/637CsKRC/pglive-allplots.gif)\n![CandleStick plot](https://i.postimg.cc/0QcmMMb0/plot-candlestick.gif)\n![live-categorized-bar.gif](https://i.postimg.cc/xqrwXXjY/live-categorized-bar.gif)\n\n# Plot speed optimizations  #\n\nScaling plot view to plotted data has a huge impact on plotting performance.\nRe-plotting might be laggy when using high update frequencies and multiple plots.    \nTo increase plotting performance, pglive introduces `LiveAxisRange`, that can be used in `LivePlotWidget`.\nUser can now specify when and how is new view of plotted data calculated.\n\nHave a look in the `live_plot_range.py` example, to see how it can be used.\n\n![Range_optimization](https://i.postimg.cc/3wrMbbTY/a.gif)\n\nIn case you want to plot wider area with LiveAxisRange you can use crop_offset_to_data flag.\nFor example, you want to store 60 seconds, display 30 seconds in a view and move view every 1 second.\nYou will have big empty space to the left without setting flag to True.\nHave a look into crop_offset_to_data example.\n\n![crop_offset_to_data](https://i.postimg.cc/90X40Ng7/Peek-2022-09-24-15-20.gif)\n\nIntroduced in *v0.4.0*\n\n# Crosshair #\n\nPglive comes with built-in Crosshair as well.\n\n![Crosshair](https://i.postimg.cc/1z75GZLV/pglive-crosshair.gif)\n\n# Leading lines #\n\nLeading line displays horizontal or vertical line (or both) at the last plotted point.  \nYou can choose it\'s color and which axis value is displayed along with it.  \n\n![Leading lines](https://i.postimg.cc/bYKQGBNp/leading-line.gif)\n\n# Axis #\n\nTo make life easier, pglive includes few axis improvements:\n\n- Colored axis line using new `axisPen` attribute\n- Time and DateTime tick format, converting timestamp into human-readable format\n\n![Crosshair](https://i.postimg.cc/8kr0L2YJ/pglive-axis.gif)\n\n# Summary #\n\n- With Pglive You\'ve got easy Thread-safe implementation of fast Live plots\n- You can use all `kwargs` specified in pyqtgraph\n- Use your pyqtgraph plots with `DataConnector` directly, no need to use specific `LivePlot` class \n- **Focus on Data Handling, not Data Plotting**',
    'author': 'Martin Domaracky',
    'author_email': 'domarm@comat.sk',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/domarm-comat/pglive',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
