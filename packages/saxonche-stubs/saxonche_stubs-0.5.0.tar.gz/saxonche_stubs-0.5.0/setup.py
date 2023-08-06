# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['saxonche-stubs']

package_data = \
{'': ['*']}

install_requires = \
['saxonche>=12.1.0,<13.0.0']

setup_kwargs = {
    'name': 'saxonche-stubs',
    'version': '0.5.0',
    'description': 'Type stubs for saxonche',
    'long_description': '# saxonche-stubs\n\nType stubs for the [saxonche](https://pypi.org/project/saxonche/) python package. This package has no functionality itself, but is merely an addition to the completion within IDEs. The basis for type annotations and comments is the documentation of [the Saxon Python API](https://www.saxonica.com/saxon-c/doc11/html/saxonc.html).\n\nAt the moment not all APIs are fully typed.\n\n## Author / Contact\n\n- [Bastian Politycki](https://github.com/Bpolitycki) – Swiss Law Sources\n',
    'author': 'Bpolitycki',
    'author_email': 'bastian.politycki@unisg.ch',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8',
}


setup(**setup_kwargs)
