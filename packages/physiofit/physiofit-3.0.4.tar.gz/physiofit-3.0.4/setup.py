# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['physiofit',
 'physiofit.base',
 'physiofit.models',
 'physiofit.tests',
 'physiofit.ui']

package_data = \
{'': ['*'],
 'physiofit': ['data/*',
               'data/KEIO_test_data/KEIO_ROBOT6_1/*',
               'data/KEIO_test_data/KEIO_ROBOT6_1/KEIO_ROBOT6_1_res/*',
               'data/KEIO_test_data/KEIO_ROBOT6_1/Multiple_Conds_Test/*',
               'data/KEIO_test_data/KEIO_ROBOT6_1/Multiple_Conds_Test/Multiple_Conds_Test_res/P53cKO_1/*',
               'data/KEIO_test_data/KEIO_ROBOT6_1/Multiple_Conds_Test/Multiple_Conds_Test_res/P53cKO_2/*',
               'data/KEIO_test_data/KEIO_ROBOT6_1/Multiple_Conds_Test/Multiple_Conds_Test_res/WT_1/*',
               'data/KEIO_test_data/KEIO_ROBOT6_1/Multiple_Conds_Test/Multiple_Conds_Test_res/WT_5/*',
               'data/KEIO_test_data/KEIO_ROBOTS_all/*',
               'data/KEIO_test_data/KEIO_ROBOTS_all/KEIO_ROBOTS_all_res/*',
               'data/KEIO_test_data/KEIO_ROBOTS_all/KEIO_ROBOTS_all_res/KEIO_ROBOT_6_1/*',
               'data/KEIO_test_data/KEIO_ROBOTS_all/KEIO_ROBOTS_all_res/KEIO_ROBOT_6_2/*',
               'data/KEIO_test_data/KEIO_ROBOTS_all/KEIO_ROBOTS_all_res/KEIO_ROBOT_6_3/*',
               'data/KEIO_test_data/KEIO_ROBOTS_all/KEIO_ROBOTS_all_res/KEIO_ROBOT_6_4/*',
               'data/KEIO_test_data/KEIO_ROBOTS_all/KEIO_ROBOTS_all_res/KEIO_ROBOT_6_5/*',
               'data/KEIO_test_data/KEIO_ROBOTS_all/KEIO_ROBOTS_all_res/KEIO_ROBOT_6_6/*',
               'data/KEIO_test_data/KEIO_ROBOTS_all/KEIO_ROBOTS_all_res/KEIO_ROBOT_6_7/*',
               'data/KEIO_test_data/KEIO_ROBOTS_all/KEIO_ROBOTS_all_res/KEIO_ROBOT_6_8/*',
               'data/KEIO_test_data/ode_test/*',
               'data/yaml_test/*']}

install_requires = \
['matplotlib>=3.7.1,<4.0.0',
 'numpy>=1.24.2,<2.0.0',
 'openpyxl>=3.1.2,<4.0.0',
 'pandas>=1.5.3,<2.0.0',
 'pyyaml>=6.0,<7.0',
 'scipy>=1.10.1,<2.0.0',
 'streamlit>=1.20.0,<2.0.0']

entry_points = \
{'console_scripts': ['physiofit = physiofit.__main__:main']}

setup_kwargs = {
    'name': 'physiofit',
    'version': '3.0.4',
    'description': 'Calculate extracellular fluxes from metabolite concentrations and biomass data',
    'long_description': '# PhysioFit\n\n[![PyPI version](https://badge.fury.io/py/physiofit.svg)](https://badge.fury.io/py/physiofit)\n[![PyPI pyversions](https://img.shields.io/pypi/pyversions/physiofit.svg)](https://pypi.python.org/pypi/physiofit/)\n[![Documentation Status](https://readthedocs.org/projects/physiofit/badge/?version=latest)](http://physiofit.readthedocs.io/?badge=latest)\n\n\n## What is PhysioFit?\n**PhysioFit is a scientific tool designed to quantify cell growth parameters and uptake & production fluxes**\n\nFluxes are estimated using various mathematical models by fitting time-course measurements of the concentration of\ncells and extracellular substrates and products. PhysioFit v3 includes by default the most common growth models, and\nadditional models can be implemented by users.\n\nIt is one of the routine tools that we use at the [MetaSys team](http://www.lisbp.fr/en/research/molecular-physiology-and-metabolism/metasys.html) \nand [MetaToul platform](http://www.metatoul.fr) in functional studies of metabolic systems.\n\nThe code is open-source, and available under a GPLv3 license. Additional information can be found in the following \n[publication](https://doi.org/10.1128/aem.00768-19).\n\nDetailed documentation can be found online at Read the Docs \n([https://physiofit.readthedocs.io/](https://physiofit.readthedocs.io/)).\n\n## Key features\n   * **calculation of growth rate and extracellular (uptake and production) fluxes**,\n   * default models for quantifying parameters in steady-state conditions (with and without lag & metabolite degradation\n     over time),\n   * **user-defined growth models**,\n   * Monte-Carlo sensitivity analysis to **estimate the precision of the calculated fluxes**,\n   * **evaluation of the goodness of fit and visual inspection of the fitted curves**,\n   * shipped as a **library** with both a **graphical** and **command line** interface,\n   * open-source, free and easy to install everywhere where Python 3 and pip run,\n   * **biologist-friendly**.\n\n## Quick-start\nPhysioFit requires Python 3.7 or higher and run on all platforms.\nPlease check [the documentation](https://physiofit.readthedocs.io/en/latest/quickstart.html) for complete\ninstallation and usage instructions.\n\nUse `pip` to **install PhysioFit from PyPi**:\n\n```bash\n$ pip install physiofit\n```\n\nThen, start the graphical interface with:\n\n```bash\n$ physiofit\n```\n\nPhysioFit is also available directly from command-line and as a Python library.\n\n## Bug and feature requests\nIf you have an idea on how we could improve PhysioFit please submit a new *issue*\nto [our GitHub issue tracker](https://github.com/MetaSys-LISBP/PhysioFit/issues).\n\n\n## Developers guide\n### Contributions\nContributions are very welcome! :heart:\n\nPlease work on your own fork,\nfollow [PEP8](https://www.python.org/dev/peps/pep-0008/) style guide,\nand make sure you pass all the tests before a pull request.\n\n### Local install with pip\nIn development mode, do a `pip install -e /path/to/PhysioFit` to install\nlocally the development version.\n\n### Build the documentation locally\nBuild the HTML documentation with:\n\n```bash\n$ cd doc\n$ make html\n```\n\nThe PDF documentation can be built locally by replacing `html` by `latexpdf`\nin the command above. You will need a recent latex installation.\n\n## How to cite\nPhysioFit: quantifying cell growth parameters and uptake and production fluxes.\nLe Grégam L., Guitton Y., Bellvert F., Jourdan F., Portais J.C., Millard P.\nIn preparation for publication\n\n## Authors\nLoïc Le Grégam, Pierre Millard\n\n## Contact\n:email: legregam@insa-toulouse.fr, millard@insa-toulouse.fr\n',
    'author': 'llegregam',
    'author_email': 'legregam@insa-toulouse.fr',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8, !=2.7.*, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*, !=3.6.*, !=3.7.*',
}


setup(**setup_kwargs)
