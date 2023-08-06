# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['elasticityproject']

package_data = \
{'': ['*']}

install_requires = \
['mayavi>=4.8.1,<5.0.0', 'numpy>=1.24.3,<2.0.0', 'vtk>=9.2.6,<10.0.0']

setup_kwargs = {
    'name': 'elasticityproject',
    'version': '0.1.1.4',
    'description': 'A collection of classes and routines to help the treatment and presentation of single and polycrystal elastic properties',
    'long_description': '# elasticityproject\n\nA collection of classes and routines to help the treatment and presentation of single and polycrystal elastic properties\n\n## Installation\n\n```bash\n$ pip install elasticityproject\n```\n\n## Usage\n\n- TODO\n\n## Contributing\n\nInterested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.\n\n## License\n\n`elasticityproject` was created by EELElasticityGroup. It is licensed under the terms of the GNU General Public License v3.0 license.\n\n## Credits\n\n`elasticityproject` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).\n',
    'author': 'EELElasticityGroup',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
