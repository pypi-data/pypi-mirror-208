# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fennel',
 'fennel._vendor',
 'fennel._vendor.astunparse',
 'fennel._vendor.certifi',
 'fennel._vendor.chardet',
 'fennel._vendor.chardet.cli',
 'fennel._vendor.chardet.metadata',
 'fennel._vendor.grandalf',
 'fennel._vendor.grandalf.utils',
 'fennel._vendor.idna',
 'fennel._vendor.jsondiff',
 'fennel._vendor.pydantic',
 'fennel._vendor.requests',
 'fennel._vendor.urllib3',
 'fennel._vendor.urllib3.contrib',
 'fennel._vendor.urllib3.contrib._securetransport',
 'fennel._vendor.urllib3.packages',
 'fennel._vendor.urllib3.packages.backports',
 'fennel._vendor.urllib3.packages.rfc3986',
 'fennel._vendor.urllib3.packages.ssl_match_hostname',
 'fennel._vendor.urllib3.util',
 'fennel.client',
 'fennel.client_tests',
 'fennel.datasets',
 'fennel.featuresets',
 'fennel.gen',
 'fennel.lib',
 'fennel.lib.aggregate',
 'fennel.lib.ascii_visualizer',
 'fennel.lib.duration',
 'fennel.lib.expectations',
 'fennel.lib.graph_algorithms',
 'fennel.lib.includes',
 'fennel.lib.includes.test_folder',
 'fennel.lib.metadata',
 'fennel.lib.schema',
 'fennel.lib.to_proto',
 'fennel.lib.window',
 'fennel.sources',
 'fennel.test_lib']

package_data = \
{'': ['*'],
 'fennel': ['tools/vendor/patches/*'],
 'fennel.client_tests': ['data/fraud_sample.csv',
                         'data/fraud_sample.csv',
                         'data/fraud_sample.csv',
                         'data/fraud_sample.csv',
                         'data/post_data.csv',
                         'data/post_data.csv',
                         'data/post_data.csv',
                         'data/post_data.csv',
                         'data/user_data.csv',
                         'data/user_data.csv',
                         'data/user_data.csv',
                         'data/user_data.csv',
                         'data/view_data_sampled.csv',
                         'data/view_data_sampled.csv',
                         'data/view_data_sampled.csv',
                         'data/view_data_sampled.csv']}

install_requires = \
['pandas>=1.0.0,<2.0.0', 'protobuf>=4.22.4,<5.0.0']

setup_kwargs = {
    'name': 'fennel-ai',
    'version': '0.15.3',
    'description': 'The modern realtime feature engineering platform',
    'long_description': "# Welcome to Fennel\n\n## The modern realtime feature engineering platform\n\n---\n\nFennel is a modern realtime feature engineering platform and has been architected from the ground up in service of three design goals.\n\n## Fennel's Three Design Goals\n1. Easy to install, learn & use - using familiar Python instead of special DSLs, simple but powerful abstractions, zero dependency installation, fully managed with zero ops, same code working for both realtime and non-realtime cases and more to make using Fennel as easy as possible\n2. Reduce cloud costs - being significantly lower on cloud costs compared to other alternatives by squeezing as much out of cloud hardware as possible [See  for how Fennel does this]\n3. Encourage best practices - native support for testing, CI/CD, versioned & immutable features, lineage tracking, enforcement of code ownership, data expectations, read/write compute separation and more to help you bring best engineering practices to feature engineering too\n\nAs a result of the architectural philosophy, Fennel ends up unlocking the following benefits:\n\n## Benefits of Fennel\n\n1. Higher development velocity: more iterations can be done in the same time leading to higher business value\n2. Lower total costs of ownership: Fennel saves costs across the board - cloud spend, bandwidth of engineers that would have gone in ops, and bandwidth of data scientists by making them more productive\n3. Higher business value via realtime features: unlocking realtime and other sophisticated features leads to better models with higher business gains\n4. Healthier codebase & more reliable features: engineering best practices like testing, immutability, code ownership etc improve code maintainability leading to more reliable data & feature\n\n## Getting Started With Fennel\n\n[Start](https://docs.fennel.ai/getting-started/quickstart) here if you want to directly dive deep into an end-to-end example.\n\nOr if you are not in a hurry, read about the main [concepts](https://docs.fennel.ai/overview/concepts) first followed by some more details about the [datasets](https://docs.fennel.ai/datasets/overview)  and [featuresets](https://docs.fennel.ai/featuresets/overview-wip) . And if you run into any issues or have any questions/feedback, you're welcome to jump into our slack channel to directly chat with the engineers building it.\nWe, the team behind Fennel, have thoroughly enjoyed building Fennel and hope learning and using Fennel brings as much delight to you as well!",
    'author': 'Fennel AI',
    'author_email': 'developers@fennel.ai',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
