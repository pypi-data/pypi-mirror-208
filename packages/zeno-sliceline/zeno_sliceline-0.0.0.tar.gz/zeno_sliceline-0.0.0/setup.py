# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sliceline']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.24.3,<2.0.0', 'scikit-learn>=1.2.2,<2.0.0']

setup_kwargs = {
    'name': 'zeno-sliceline',
    'version': '0.0.0',
    'description': '✂️ Fast slice finding for Machine Learning model debugging.',
    'long_description': 'Sliceline\n=========\n\nSliceline is a Python library for fast slice finding for Machine\nLearning model debugging.\n\nIt is an implementation of `SliceLine: Fast, Linear-Algebra-based Slice\nFinding for ML Model\nDebugging <https://mboehm7.github.io/resources/sigmod2021b_sliceline.pdf>`__,\nfrom Svetlana Sagadeeva and Matthias Boehm of Graz University of\nTechnology.\n\n👉 Getting started\n------------------\n\nGiven an input dataset ``X`` and a model error vector ``errors``,\nSliceLine finds the top slices in ``X`` that identify where a ML model\nperforms significantly worse.\n\nYou can use sliceline as follows:\n\n.. code:: python\n\n   from sliceline.slicefinder import Slicefinder\n\n   slice_finder = Slicefinder()\n\n   slice_finder.fit(X, errors)\n\n   print(slice_finder.top_slices_)\n\n   X_trans = slice_finder.transform(X)\n\nWe invite you to check the `demo\nnotebooks <https://github.com/DataDome/sliceline/blob/main/notebooks>`__\nfor a more thorough tutorial:\n\n1. Implementing Sliceline on Titanic dataset\n2. Implementing Sliceline on California housing dataset\n\n🛠 Installation\n---------------\n\nSliceline is intended to work with **Python 3.7 or above**. Installation\ncan be done with ``pip``:\n\n.. code:: sh\n\n   pip install sliceline\n\nThere are `wheels\navailable <https://pypi.org/project/sliceline/#files>`__ for Linux,\nMacOS, and Windows, which means that you most probably won’t have to\nbuild Sliceline from source.\n\nYou can install the latest development version from GitHub as so:\n\n.. code:: sh\n\n   pip install git+https://github.com/DataDome/sliceline --upgrade\n\nOr, through SSH:\n\n.. code:: sh\n\n   pip install git+ssh://git@github.com/datadome/sliceline.git --upgrade\n\n🔗 Useful links\n---------------\n\n-  `Documentation <https://sliceline.readthedocs.io/en/stable/>`__\n-  `Package releases <https://pypi.org/project/sliceline/#history>`__\n-  `SliceLine paper <https://mboehm7.github.io/resources/sigmod2021b_sliceline.pdf>`__\n\n👐 Contributing\n---------------\n\nFeel free to contribute in any way you like, we’re always open to new\nideas and approaches.\n\n-  `Open a\n   discussion <https://github.com/DataDome/sliceline/discussions/new>`__\n   if you have any question or enquiry whatsoever. It’s more useful to\n   ask your question in public rather than sending us a private email.\n   It’s also encouraged to open a discussion before contributing, so\n   that everyone is aligned and unnecessary work is avoided.\n-  Feel welcome to `open an\n   issue <https://github.com/DataDome/sliceline/issues/new/choose>`__ if\n   you think you’ve spotted a bug or a performance issue.\n\nPlease check out the `contribution\nguidelines <https://github.com/DataDome/sliceline/blob/main/CONTRIBUTING.md>`__\nif you want to bring modifications to the code base.\n\n📝 License\n----------\n\nSliceline is free and open-source software licensed under the `3-clause BSD license <https://github.com/DataDome/sliceline/blob/main/LICENSE>`__.\n',
    'author': 'Antoine de Daran',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/DataDome/sliceline',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8',
}


setup(**setup_kwargs)
