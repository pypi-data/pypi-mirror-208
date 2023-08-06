# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['quant_invest_lab']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4.12.2,<5.0.0',
 'fitter>=1.5.2,<2.0.0',
 'kucoin-python>=1.0.11,<2.0.0',
 'matplotlib>=3.7.1,<4.0.0',
 'nbformat>=5.8.0,<6.0.0',
 'numpy>=1.24.3,<2.0.0',
 'pandas>=2.0.1,<3.0.0',
 'plotly>=5.14.1,<6.0.0',
 'scikit-learn>=1.2.2,<2.0.0',
 'scipy>=1.10.1,<2.0.0',
 'seaborn>=0.12.2,<0.13.0',
 'statsmodels>=0.14.0,<0.15.0',
 'ta>=0.10.2,<0.11.0',
 'tqdm>=4.65.0,<5.0.0']

setup_kwargs = {
    'name': 'quant-invest-ab',
    'version': '0.1.0',
    'description': 'Quant Invest Lab is a python package to help you to do some quantitative experiments, while trying to learn or build quantitative investment solutions. This project was initially my own set of functionnalities but I decided to build a package for that and sharing it as open source project.',
    'long_description': '# Quant Invest Lab\n**Quant Invest Lab** is a project aimed to provide a set of basic tools for quantitative experiments. By quantitative experiment I mean trying to build you own set of investments solution. The project is still in its early stage, but I hope it will grow in the future.\n\nInitially this project was aimed to be a set of tools for my own experiments, but I decided to make it open source. Of courses it already exists some awesome packages, more detailed, better suited for some use cases. But I hope it will be useful for someone else. Feel free to use it, modify it and contribute to it.*\n## Main features\n- **Data**: download data from external data provider without restriction on candle stick, the main provider is kucoin for now (currently only crypto data are supported).\n- **Backtesting**: backtest your trading strategy (Long only for now but soon short and leverage) on historical data for different timeframe. Optimize you take profit, stop loss. Access full metrics of your strategy.\n- **Indicators**: a set of indicators to help you build your strategy.\n- **Portfolio**: a set of portfolio optimization tools to help you build your portfolio.\n- **Simulation**: simulate your data based on real data using statistics to get a better understanding of its behavior during backtesting.\n- **Metrics**: a set of metrics to help you evaluate your strategy through performances and risks.\n\n## Installation\nTo install **Quant Invest Lab** through pip, run the following command:\n```bash\npip install quant-invest-lab --upgrade\n```\nYou can install it using poetry the same way :\n```bash\npoetry add quant-invest-lab\n```\n\n# Basic examples\n## Backtest a basic EMA crossover strategy\n```python\n``` \n\n## Next steps create official docs and add more examples\n## Disclaimer\nThis package is only for educational purpose or experimentation it is not intended to be used in production. I am not responsible for any loss of money you may have using this package. Use it at your own risk.',
    'author': 'BaptisteZloch',
    'author_email': 'bzloch@hotmail.fr',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.12',
}


setup(**setup_kwargs)
