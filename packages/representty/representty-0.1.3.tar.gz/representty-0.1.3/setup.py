# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['representty']
install_requires = \
['ipython', 'rich>=13.3.1,<14.0.0']

entry_points = \
{'console_scripts': ['rtty = representty:just_call_the_script']}

setup_kwargs = {
    'name': 'representty',
    'version': '0.1.3',
    'description': 'Tiny presentation tool based on rich and markdown',
    'long_description': '# representty\n\n`representty` is a tiny presentation framework. TL;DR: You write your slides in\nMarkdown, `rich` renders individual slides, and the whole thing happens in an\nIPython shell.\n\n## File Format\n\nA slide deck is mostly a Markdown file. Individual slides are seperated by a\nbunch of equals signs.\n\nAdditionally, you can start a line with:\n\n- `//`: comment; the line is ignored (unless the environment variable\n  `PRACTICE` is set).\n- `!`: special instruction. The line is not included in the output, but can do\n  a variety of things:\n    - `!!some command`: execute the command with `os.system()` the first time\n      this slide is visited.\n    - `!import somemodule`: silently import the given module.\n    - `!set flag`/`!unset flag`: set/unset a named flag. These can influence\n      `representty` behaviour. See [flags](#flags).\n    - `!setlocal flag`/`!unsetlocal flag`: (un)set a flag, but reset to\n      original value at the end of the slide.\n\nPython code blocks (language starts with `py`) are not just rendered, but also\nexecuted.\n\n## Commands\n\nThe presenter is dropped into a more-or-less normal IPython shell. A few\nsingle-letter commands exist which control the slide show:\n\n- `d`: (Re)draw the current slide.\n- `n`: Go to the next slide.\n- `p`: Go to the previous slide.\n- `q`: Quit.\n- `g`: Go to a numbered slide (you will be prompted for a slide number).\n- `s`: Go to a slide by searching for a keyword (you will be prompted).\n\n## Flags\n\n- `exec`: whether to execute Python code in code blocks. Default: set.\n- `alwaysexec`: Always execute shell commands (`!!`), rather than just at the\n  first printing of the slide. Default: unset.\n',
    'author': 'L3viathan',
    'author_email': 'git@l3vi.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/L3viathan/representty',
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
