# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['corallium', 'corallium.loggers', 'corallium.loggers.structlog_logger']

package_data = \
{'': ['*']}

install_requires = \
['beartype>=0.12.0', 'pydantic>=1.10.4', 'rich>=12.6.0']

extras_require = \
{':python_version < "3.11"': ['tomli>=2.0.1']}

setup_kwargs = {
    'name': 'corallium',
    'version': '0.2.2',
    'description': 'Shared functionality for calcipy-ecosystem',
    'long_description': '# corallium\n\nShared functionality for the calcipy-ecosystem.\n\n## Installation\n\n1. `poetry add corallium`\n\n1. Take advantage of the logger or other common functionality\n\n    ```sh\n    form corallium.log import logger\n\n    logger.info(\'Hello!\')\n    ```\n\n## Usage\n\n<!-- < TODO: Show an example (screenshots, terminal recording, etc.) >\n\n- **log**: TBD\n- **pretty_process**: TBD\n- **shell**: TBD\n- **file_helpers**: TBD\n- **tomllib**: This is a lightweight wrapper to backport `tomli` in place of `tomllib` until we can use Python >3.11. Use with `from corallium.tomllib import tomllib`\n- **dot_dict**: has one function `ddict`, which is a light-weight wrapper around whatever is the most [maintained dotted-dictionary package in Python](https://pypi.org/search/?q=dot+accessible+dictionary&o=). Dotted dictionaries can sometimes improve code readability, but they aren\'t a one-size fits all solution. Sometimes `attr.s` or `dataclass` are more appropriate.\n    - The benefit of this wrapper is a stable interface that can be replaced with better internal implementations, such [Bunch](https://pypi.org/project/bunch/), [Chunk](https://pypi.org/project/chunk/), [Munch](https://pypi.org/project/munch/), [flexible-dotdict](https://pypi.org/project/flexible-dotdict/), [classy-json](https://pypi.org/project/classy-json/), and now [Python-Box](https://pypi.org/project/python-box/)\n -->\n\nFor more example code, see the [scripts] directory or the [tests].\n\n## Project Status\n\nSee the `Open Issues` and/or the [CODE_TAG_SUMMARY]. For release history, see the [CHANGELOG].\n\n## Contributing\n\nWe welcome pull requests! For your pull request to be accepted smoothly, we suggest that you first open a GitHub issue to discuss your idea. For resources on getting started with the code base, see the below documentation:\n\n- [DEVELOPER_GUIDE]\n- [STYLE_GUIDE]\n\n## Code of Conduct\n\nWe follow the [Contributor Covenant Code of Conduct][contributor-covenant].\n\n### Open Source Status\n\nWe try to reasonably meet most aspects of the "OpenSSF scorecard" from [Open Source Insights](https://deps.dev/pypi/corallium)\n\n## Responsible Disclosure\n\nIf you have any security issue to report, please contact the project maintainers privately. You can reach us at [dev.act.kyle@gmail.com](mailto:dev.act.kyle@gmail.com).\n\n## License\n\n[LICENSE]\n\n[changelog]: https://corallium.kyleking.me/docs/CHANGELOG\n[code_tag_summary]: https://corallium.kyleking.me/docs/CODE_TAG_SUMMARY\n[contributor-covenant]: https://www.contributor-covenant.org\n[developer_guide]: https://corallium.kyleking.me/docs/DEVELOPER_GUIDE\n[license]: https://github.com/kyleking/corallium/blob/main/LICENSE\n[scripts]: https://github.com/kyleking/corallium/blob/main/scripts\n[style_guide]: https://corallium.kyleking.me/docs/STYLE_GUIDE\n[tests]: https://github.com/kyleking/corallium/blob/main/tests\n',
    'author': 'Kyle King',
    'author_email': 'dev.act.kyle@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/kyleking/corallium',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8.12,<4.0.0',
}


setup(**setup_kwargs)
