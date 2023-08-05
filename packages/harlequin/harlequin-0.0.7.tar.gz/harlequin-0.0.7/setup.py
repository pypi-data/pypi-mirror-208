# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['harlequin', 'harlequin.tui', 'harlequin.tui.components']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.1.3,<9.0.0',
 'duckdb>=0.7.1,<0.8.0',
 'shandy-sqlfmt>=0.18.0,<0.19.0',
 'textual>=0.22.3,<0.25.0']

entry_points = \
{'console_scripts': ['harlequin = harlequin.cli:harlequin']}

setup_kwargs = {
    'name': 'harlequin',
    'version': '0.0.7',
    'description': 'A Text User Interface for DuckDB',
    'long_description': '# harlequin\nA Terminal-based SQL IDE for DuckDB.\n\n![harlequin TUI](harlequinv004.gif)\n\n(A Harlequin is also a [pretty duck](https://en.wikipedia.org/wiki/Harlequin_duck).)\n\n![harlequin duck](harlequin.jpg)\n\n## Installing Harlequin\n\nUse `pip` or `pipx`:\n\n```bash\npipx install harlequin\n```\n\n> **Tip:**\n>\n> You can run invoke directly with [`pipx run`](https://pypa.github.io/pipx/examples/#pipx-run-examples) anywhere that `pipx` is installed. For example:\n> - `pipx run harlequin --help`\n> - `pipx run harlequin ./my.duckdb`\n\n## Using Harlequin\n\nTo open a DuckDB database file:\n\n```bash\nharlequin "path/to/duck.db"\n```\n\nTo open an in-memory DuckDB session, run Harlequin with no arguments:\n\n```bash\nharlequin\n```\n\nWhen Harlequin is open, you can view the schema of your DuckDB database in the left sidebar.\n\nTo run a query, enter your code in the main textarea, then press Ctrl+Enter. You should see the data appear in the pane below.\n\nYou can press Tab or use your mouse to change the focus between the panes.\n\nWhen the focus is on the data pane, you can use your arrow keys or mouse to select different cells.\n\nPress Ctrl+c to quit and return to your shell.\n\n### Running Harlequin in a Container\n\nWithout a database file:\n\n```bash\ndocker run ghcr.io/tconbeer/harlequin:latest\n```\n\nMounting a database file `./foo.db` into the container\'s working directory, `/data`:\n\n```bash\ndocker run -v $(pwd)/foo.db:/data/bar.db ghcr.io/tconbeer/harlequin:latest harlequin bar.db\n```\n',
    'author': 'Ted Conbeer',
    'author_email': 'tconbeer@users.noreply.github.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
