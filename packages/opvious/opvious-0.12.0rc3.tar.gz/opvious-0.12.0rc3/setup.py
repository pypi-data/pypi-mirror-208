# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['opvious',
 'opvious.client',
 'opvious.data',
 'opvious.executors',
 'opvious.specifications',
 'opvious.specifications.model']

package_data = \
{'': ['*']}

install_requires = \
['backoff>=2.2,<3.0', 'humanize>=4.4.0,<5.0.0', 'pandas>=1.4,<2.0']

extras_require = \
{'aio': ['aiohttp>=3.8,<4.0', 'Brotli>=1.0.9,<2.0.0']}

setup_kwargs = {
    'name': 'opvious',
    'version': '0.12.0rc3',
    'description': 'Opvious Python SDK',
    'long_description': '# Opvious Python SDK  [![CI](https://github.com/opvious/sdk.py/actions/workflows/ci.yml/badge.svg)](https://github.com/opvious/sdk.py/actions/workflows/ci.yml) [![Pypi badge](https://badge.fury.io/py/opvious.svg)](https://pypi.python.org/pypi/opvious/)\n\nAn optimization SDK for solving linear, mixed-integer, and quadratic models\n\n```python\nimport opvious\n\nclient = opvious.Client.from_environment()\n\n# Solve a portfolio selection optimization model\nresponse = await client.run_solve(\n    specification=opvious.InlineSpecification([\n      r"""\n          We find an allocation of assets which minimizes risk while satisfying\n          a minimum expected return:\n\n          + A collection of assets: $\\S^d_{asset}: A$\n          + Covariances: $\\S^p_{covariance}: c \\in \\mathbb{R}^{A \\times A}$\n          + Expected return: $\\S^p_{expectedReturn}: m \\in \\mathbb{R}^A$\n          + Minimum desired return: $\\S^p_{desiredReturn}: r \\in \\mathbb{R}$\n\n          The only output is the allocation per asset\n          $\\S^v_{allocation}: \\alpha \\in [0,1]^A$ chosen to minimize risk:\n          $\\S^o_{risk}: \\min \\sum_{a, b \\in A} c_{a,b} \\alpha_a \\alpha_b$.\n\n          Subject to the following constraints:\n\n          + $\\S^c_{atLeastMinimumReturn}: \\sum_{a \\in A} m_a \\alpha_a \\geq r$\n          + $\\S^c_{totalAllocation}: \\sum_{a \\in A} \\alpha_a = 1$\n      """\n    ]),\n    parameters={\n        "covariance": {\n            ("AAPL", "AAPL"): 0.08,\n            # ...\n        },\n        "expectedReturn": {\n            "AAPL": 0.07,\n            # ..\n        },\n        "desiredReturn": 0.05,\n    },\n    assert_feasible=True,\n)\n\noptimal_allocation = response.outputs.variable("allocation")\n```\n\nTake a look at https://opvious.readthedocs.io for the full documentation or\n[these notebooks][notebooks] to see it in action.\n\n[notebooks]: https://github.com/opvious/examples/tree/main/notebooks\n',
    'author': 'Opvious Engineering',
    'author_email': 'oss@opvious.io',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/opvious/sdk.py',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.9,<3.12',
}


setup(**setup_kwargs)
