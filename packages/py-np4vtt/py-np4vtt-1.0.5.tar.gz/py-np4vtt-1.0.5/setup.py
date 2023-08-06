# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['py_np4vtt']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.5.1,<4.0.0',
 'numdifftools>=0.9.40,<0.10.0',
 'pandas>=1.3.1,<2.0.0',
 'scikit-learn>=1.0.2,<2.0.0',
 'scipy>=1.7.1,<2.0.0']

setup_kwargs = {
    'name': 'py-np4vtt',
    'version': '1.0.5',
    'description': 'Python library providing NonParametric models for Value of Travel Time analysis',
    'long_description': '# NP4VTT\n\nNP4VTT is a Python package that enables researchers to estimate and compare nonparametric models in a fast and convenient way. It comprises five nonparametric models for estimating the VTT distribution from data coming from two-attribute-two-alternative stated choice experiments:\n\n   * Local constant model  (Fosgerau, 2006, 2007)\n   * Local logit (Fosgerau, 2007)\n   * Rouwendal model (Rouwendal et al., 2010)\n   * Artificial Neural Network (ANN) based VTT model (van Cranenburgh & Kouwenhoven, 2021)\n   * Logistic Regression based VTT model (van Cranenburgh & Kouwenhoven, 2021)\n\nAdditionally, a Random Valuation model (Ojeda-Cabral, 2006) is included for benchmarking purposes\n\n## Installation steps\n\n* Use `pip` to install the `py-np4vtt` library normally:\n    - `python3 -m pip install py-np4vtt`\n\n\n## Examples\n\nWe provide Jupyter Notebooks that show how to configure and estimate each model included in NP4VTT:\n\n   * Local constant model: [link](https://gitlab.tudelft.nl/np4vtt/py-np4vtt/-/blob/master/examples/lconstant.ipynb)\n   * Local logit: [link](https://gitlab.tudelft.nl/np4vtt/py-np4vtt/-/blob/master/examples/loclogit.ipynb)\n   * Rouwendal model: [link](https://gitlab.tudelft.nl/np4vtt/py-np4vtt/-/blob/master/examples/rouwendal.ipynb)\n   * ANN-based VTT model: [link](https://gitlab.tudelft.nl/np4vtt/py-np4vtt/-/blob/master/examples/ann.ipynb)\n   * Logistic Regression-based VTT model: [link](https://gitlab.tudelft.nl/np4vtt/py-np4vtt/-/blob/master/examples/logistic.ipynb)\n\nThese examples guide the user through the process of loading a dataset, estimating a nonparametric model, and visualising the VTT distribution using scatter and histogram plots. We use the Norwegian 2009 VTT data to illustrate each example.\n\n**Take, for example, the VTT distribution from the Rouwendal model using NP4VTT:**\n\n![VTT distribution from the Rouwendal model using NP4VTT](https://gitlab.tudelft.nl/np4vtt/py-np4vtt/-/raw/master/examples/outcomes/rouwendal.png)\n\n## References\n\n   * Fosgerau, M. (2006). Investigating the distribution of the value of travel time savings. Transportation Research Part B: Methodological, 40(8), 688–707. https://doi.org/10.1016/j.trb.2005.09.007\n   * Fosgerau, M. (2007). Using nonparametrics to specify a model to measure the value of travel time. Transportation Research Part A: Policy and Practice, 41(9), 842–856. https://doi.org/10.1016/j.tra.2006.10.004\n   * Rouwendal, J., de Blaeij, A., Rietveld, P., & Verhoef, E. (2010). The information content of a stated choice experiment: A new method and its application to the value of a statistical life. Transportation Research Part B: Methodological, 44(1), 136–151. https://doi.org/10.1016/j.trb.2009.04.006\n   * Ojeda-Cabral, M., Batley, R., & Hess, S. (2016). The value of travel time: Random utility versus random valuation. Transportmetrica A: Transport Science, 12(3), 230–248. https://doi.org/10.1080/23249935.2015.1125398\n   * van Cranenburgh, S., & Kouwenhoven, M. (2021). An artificial neural network based method to uncover the value-of-travel-time distribution. Transportation, 48(5), 2545–2583. https://doi.org/10.1007/s11116-020-10139-3',
    'author': 'José Ignacio Hernández',
    'author_email': 'J.I.Hernandez@tudelft.nl',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.tudelft.nl/np4vtt/py-np4vtt',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<=3.10',
}


setup(**setup_kwargs)
