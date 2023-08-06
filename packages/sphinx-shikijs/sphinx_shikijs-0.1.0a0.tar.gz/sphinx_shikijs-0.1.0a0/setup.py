# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['sphinx_shikijs']

package_data = \
{'': ['*']}

install_requires = \
['sphinx>=6.1.3,<7.0.0']

setup_kwargs = {
    'name': 'sphinx-shikijs',
    'version': '0.1.0a0',
    'description': '',
    'long_description': '# sphinx-shikijs\n\nUse [Shiki](https://shiki.matsu.io/) to highlight code.\n\n## Installation\n\n```\npip install sphinx-shikijs\n```\n\nThen, add `sphinx_shikijs` to your extensions in `conf.py`:\n\n```python\nextensions = [\n  # ...\n  "sphinx_shikijs",\n]\n```\n\n## Configuration\n\n| Setting | Default | Description |\n| --- | --- | --- |\n| shikijs_mode | `"cli"` | Either `"cli"` or `"browser"`. In browser mode, this will load Shiki from [unpkg](https://unpkg.com/shiki@0.14.1/dist/index.unpkg.iife.js). |\n| shikijs_path | `"shiki-cli"` | Path to a Shiki CLI executable. |\n| shikijs_highlight_theme | `"dark-plus"` | A Shiki theme. For possible themes, see [here](https://github.com/shikijs/shiki/blob/main/docs/themes.md) |',
    'author': 'Ashley Trinh',
    'author_email': 'itsashley@hey.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.11,<4.0',
}


setup(**setup_kwargs)
