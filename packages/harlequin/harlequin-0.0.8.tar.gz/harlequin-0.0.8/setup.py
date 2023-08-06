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
    'version': '0.0.8',
    'description': 'A Text User Interface for DuckDB',
    'long_description': '# harlequin\nA Terminal-based SQL IDE for DuckDB.\n\n![harlequin TUI](harlequinv004.gif)\n\n(A Harlequin is also a [pretty duck](https://en.wikipedia.org/wiki/Harlequin_duck).)\n\n![harlequin duck](harlequin.jpg)\n\n## Installing Harlequin\n\nAfter installing Python 3.8 or above, install Harlequin using `pip` or `pipx` with:\n\n```bash\npipx install harlequin\n```\n\n> **Tip:**\n>\n> You can run invoke directly with [`pipx run`](https://pypa.github.io/pipx/examples/#pipx-run-examples) anywhere that `pipx` is installed. For example:\n> - `pipx run harlequin --help`\n> - `pipx run harlequin ./my.duckdb`\n\n\n## Running Harlequin in a Container\n\nWithout a database file:\n\n```bash\ndocker run ghcr.io/tconbeer/harlequin:latest\n```\n\nMounting a database file `./foo.db` into the container\'s working directory, `/data`:\n\n```bash\ndocker run -v $(pwd)/foo.db:/data/bar.db ghcr.io/tconbeer/harlequin:latest harlequin bar.db\n```\n\n## Using Harlequin\n\nFrom any shell, to open a DuckDB database file:\n\n```bash\nharlequin "path/to/duck.db"\n```\n\nTo open an in-memory DuckDB session, run Harlequin with no arguments:\n\n```bash\nharlequin\n```\n\n### Viewing the Schema of your Database\n\nWhen Harlequin is open, you can view the schema of your DuckDB database in the left sidebar. You can use your mouse or the arrow keys + enter to navigate the tree. The tree shows schemas, tables/views and their types, and columns and their types.\n\n### Editing a Query\n\nThe main query editor is a full-featured text editor, with features including syntax highlighting, auto-formatting with ``ctrl + ` ``, text selection, copy/paste, and more.\n\nYou can save the query currently in the editor with `ctrl + s`. You can open a query in any text or .sql file with `ctrl + o`.\n\n### Running a Query and Viewing Results\n\nTo run a query, press `ctrl + enter`. Up to 50k records will be loaded into the results pane below the query editor. When the focus is on the data pane, you can use your arrow keys or mouse to select different cells.\n\n### Exiting Harlequin\n\nPress `ctrl + q` to quit and return to your shell.',
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
