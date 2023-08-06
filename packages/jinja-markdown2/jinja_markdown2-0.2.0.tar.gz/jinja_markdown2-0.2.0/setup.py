# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jinja_markdown2']

package_data = \
{'': ['*']}

install_requires = \
['jinja2>=3.1.2,<4.0.0', 'markdown2>=2.4.8,<3.0.0']

setup_kwargs = {
    'name': 'jinja-markdown2',
    'version': '0.2.0',
    'description': '',
    'long_description': "# jinja-markdown2\n\nInspired by the original [jinja-markdown](https://github.com/jpsca/jinja-markdown).\n\nUses `jinja2` + `markdown2` to render markdown code _after_ jinja's templating magic\n(variable interpolation, etc.) is done. Critical difference between the naive:\n\n    Markdown ->  HTML -> Jinja\n\nNotice, the above processes the markdown _first_ and jinja templating _last_. Whilst\nthis approach technically works, it results in a myriad of problems with the resultant\nHTML that markdown2 formulates.\n\nThe flow is then:\n\n    HTML -> Jinja -> Markdown\n\n## Usage\n\nPython:\n\n```python\n...\nfrom jinja_markdown2 import MarkdownExtension\n\njinja_env = ...\njinja_env.add_extension(MarkdownExtension)\n...\n```\n\nMarkdown:\n\n```html\n{% markdown %}\n\n## Hello {{ world_name }}\n\n{% endmarkdown %}\n```\n",
    'author': 'Mike Babb',
    'author_email': 'mike7400@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/mkbabb/jinja-markdown2',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
