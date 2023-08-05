# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wanda', 'wanda.utils']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=9.1.0,<10.0.0',
 'appdirs>=1.4.4,<2.0.0',
 'cloudscraper>=1.2.60,<2.0.0',
 'colorthief>=0.2.1,<0.3.0',
 'filetype>=1.0.13,<2.0.0',
 'lxml>=4.9.0,<5.0.0',
 'musicbrainzngs>=0.7.1,<0.8.0',
 'screeninfo>=0.8,<0.9']

entry_points = \
{'console_scripts': ['wanda = wanda.wanda:run']}

setup_kwargs = {
    'name': 'wanda',
    'version': '0.61.3',
    'description': 'Set wallpapers with keywords or randomly',
    'long_description': '# wanda\nScript to set wallpaper using keyword or randomly\n\n[![Codacy Badge](https://app.codacy.com/project/badge/Grade/e5aacd529ce04f3fb8c0f9ce6a3bdd9e)](https://www.codacy.com/gh/ksyko/wanda/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=ksyko/wanda&amp;utm_campaign=Badge_Grade)[![PyPI](https://img.shields.io/pypi/v/wanda)](https://pypi.org/project/wanda/)\n[![PyPI - Downloads](https://img.shields.io/pypi/dm/wanda)](https://pypistats.org/packages/wanda)\n[![PyPI - License](https://img.shields.io/pypi/l/wanda)](https://tldrlegal.com/license/mit-license)\n[![codecov](https://codecov.io/gl/kshib/wanda/branch/main/graph/badge.svg?token=L88CXOYRTW)](https://codecov.io/gl/kshib/wanda)\n\n## Installation / Update\n```\npip install wanda -U\n```\n\nOn android (with termux):\n```\npkg in libxml2 libxslt libjpeg-turbo\npip install wanda -U\n```\n\nFor issues installing pillow refer this [document](https://pillow.readthedocs.io/en/stable/installation.html)\n\n\n## Usage\n```\n# Set randomly\nwanda\n\n# Set from a keyword \nwanda -t mountain\n\n# Set from a source\nwanda -s wallhaven\n\n# Set from a source \nwanda -s wallhaven -t japan\n```\n`wanda -h` for more details\n\n## Notes\n- By default, the source is [unsplash](https://unsplash.com).\n- Some sources may have inapt images. Use them at your own risk.\n\n## Supported sources\n\n- [4chan](https://boards.4chan.org) via [Rozen Arcana](https://archive-media.palanq.win)\n- [500px](https://500px.com)\n- [artstation](https://artstation.com)\n- [imgur](https://imgur.com) via [rimgo](https://rimgo.pussthecat.org)\n- [earthview](https://earthview.withgoogle.com)\n- local\n- [picsum](https://picsum.photos)\n- [reddit](https://reddit.com)\n- [unsplash](https://unsplash.com)\n- [wallhaven](https://wallhaven.cc)\n\n## Build\n[python](https://www.python.org/downloads) and [poetry](https://python-poetry.org) are needed\n```\ngit clone https://github.com/ksh-b/wanda.git\ncd wanda\npoetry install\npoetry build\npoetry run wanda\n```\n\n## Uninstall\n```\npip uninstall wanda\n```\n\n## License\nMIT\n',
    'author': 'kshib',
    'author_email': 'ksyko@pm.me',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/ksh-b/wanda',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
