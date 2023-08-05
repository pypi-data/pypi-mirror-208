# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sigma', 'sigma.analyze', 'sigma.cli']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.3,<9.0.0',
 'colorama>=0.4.6,<0.5.0',
 'prettytable>=3.1.1,<4.0.0',
 'pysigma>=0.9.9,<0.10.0']

entry_points = \
{'console_scripts': ['sigma = sigma.cli.main:main']}

setup_kwargs = {
    'name': 'sigma-cli',
    'version': '0.7.5',
    'description': 'Sigma Command Line Interface (conversion, check etc.) based on pySigma',
    'long_description': '# Sigma Command Line Interface\n\n![Tests](https://github.com/SigmaHQ/sigma-cli/actions/workflows/test.yml/badge.svg)\n![Coverage Badge](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/thomaspatzke/0c868df261d4a5d5a1dafe71b1557d69/raw/SigmaHQ-sigma-cli.json)\n![Status](https://img.shields.io/badge/Status-pre--release-orange)\n\nThis is the Sigma command line interface using the [pySigma](https://github.com/SigmaHQ/pySigma) library to manage, list\nand convert Sigma rules into query languages.\n\n## Getting Started\n\n### Installation\n\nThe easiest way to install the Sigma CLI is via *pipx* or *pip*. For this purpose run one of the following:\n\n```\npython -m pipx install sigma-cli\npython -m pip install sigma-cli\n```\non macOS use\n```\npython3 -m pip install sigma-cli\n```\n\nAnother way is to run this from source in a virtual environment managed by [Poetry](https://python-poetry.org/docs/basic-usage/):\n\n```\ngit clone https://github.com/SigmaHQ/sigma-cli.git\ncd sigma-cli\npoetry install\npoetry shell\n```\n\n### Usage\n\nThe CLI is available as *sigma* command. A typical invocation is:\n\n```\nsigma convert -t <backend> -p <processing pipeline 1> -p <processing pipeline 2> [...] <directory or file>\n```\n\nE.g. to convert process creation Sigma rules from a directory into Splunk queries for Sysmon logs run:\n\n```\nsigma convert -t splunk -p sysmon sigma/rules/windows/process_creation\n```\n\nRequired backends must be installed using the following command prior to conducting conversions.\n\n```\nsigma plugin install <backend>\n```\nE.g. to install the splunk backend run:\n```\nsigma plugin install splunk\n```\n\nAvailable conversion backends and processing pipelines can be listed with `sigma list`. \nUse `-O` or `--backend-option` for passing options to the backend as key=value pairs (`-O testparam=123`) .\nThis backend option parameter can be used multiple times (`-O first=123 -O second=456`).\n\nBackends can support different output formats, e.g. plain queries and a file that can be imported into the target\nsystem. These formats can be listed with `sigma list formats <backend>` and specified for conversion with the `-f`\noption.\n\nIn addition, an output file can be specified with `-o`.\n\nExample for output formats and files:\n\n```\nsigma convert -t splunk -f savedsearches -p sysmon -o savedsearches.conf sigma/rules/windows/process_creation\n```\n\nOutputs a Splunk savedsearches.conf containing the converted searches.\n\n### Integration of Backends and Pipelines\n\nBackends and pipelines can be integrated by adding the corresponding packages as dependency with:\n\n```\npoetry add <package name>\n```\n\nA backend has to be added to the `backends` dict in `sigma/cli/backends.py` by creation of a `Backend` named tuple with\nthe following parameters:\n\n* The backend class.\n* A display name shown to the user in the targets list (`sigma list targets`).\n* A dict that maps output format names (used in `-f` parameter) to descriptions of the formats that are shown in the\n  format list (`sigma list formats <backend>`). The formats must be supported by the backend!\n\nThe dict key is the name used in the `-t` parameter.\n\nA processing pipeline is defined in the `pipelines` variable dict in `sigma/cli/pipelines.py`. The variable contains a\n`ProcessingPipelineResolver` that is instantiated with a dict that maps identifiers that can\nbe used in the `-p` parameter to functions that return `ProcessingPipeline` objects. The descriptive text shown in the pipeline list (`sigma list pipelines`) is provided from\nthe `name` attribute of the `ProcessingPipeline` object.\n\n## Maintainers\n\nThe project is currently maintained by:\n\n- Thomas Patzke <thomas@patzke.org>\n',
    'author': 'Thomas Patzke',
    'author_email': 'thomas@patzke.org',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/SigmaHQ/sigma-cli',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
