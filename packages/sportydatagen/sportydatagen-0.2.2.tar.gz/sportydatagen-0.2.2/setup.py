# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sportydatagen', 'sportydatagen.cluster', 'sportydatagen.plot']

package_data = \
{'': ['*']}

install_requires = \
['niapy>=2.0.5,<3.0.0',
 'numpy>=1.24.2,<2.0.0',
 'pandas',
 'scikit-learn>=1.2.2,<2.0.0',
 'sport-activities-features>=0.3.12,<0.4.0']

setup_kwargs = {
    'name': 'sportydatagen',
    'version': '0.2.2',
    'description': 'Sports activity generator module',
    'long_description': '# SportyDataGen -- Generator of Endurance Sports Activity Collections (datasets)\n\n## About\n\nSportyDataGen Library is a Python library designed to work with sport GPX and TCX files. It allows users to easily convert these file types into CSV format, extract feature data, and return random data based on specified conditions.\n\nIt aims to help researchers to create datasets for machine learning and data mining applications.\n\n## Features\n* Conversion of GPX and TCX files to CSV format\n* Extraction of feature data from sport files, including GPS coordinates, ascent, heart rate, distance and more\n* Merge of multiple csv files into a single dataset\n* Random selection of data based on the number of rows, percentage of rows in a file or custom conditions\n* Integration with Python scripts to provide an efficient data processing pipeline\n\n## Reference Papers:\n\nIdeas are based on the following research papers:\n\n[1] Fister, I., Jr.; Vrbančič, G.; Brezočnik, L.; Podgorelec, V.; Fister, I. [SportyDataGen: An Online Generator of Endurance Sports Activity Collections](https://www.iztok-jr-fister.eu/static/publications/225.pdf). In Proceedings of the Central European Conference on Information and Intelligent Systems, Varaždin, Croatia, 19–21 September 2018; pp. 171–178.\n\n## License\n\nThis package is distributed under the MIT License. This license can be found online at <http://www.opensource.org/licenses/MIT>.\n\n## Disclaimer\n\nThis framework is provided as-is, and there are no guarantees that it fits your purposes or that it is bug-free. Use it at your own risk!\n',
    'author': 'Rok Kukovec',
    'author_email': 'rok.kukovec1@student.um.si',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/firefly-cpp/sportydatagen',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.11,<4.0',
}


setup(**setup_kwargs)
