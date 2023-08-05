# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['join_eos_exif']

package_data = \
{'': ['*']}

install_requires = \
['PyQt6>=6.4.0,<7.0.0', 'numpy>=1.23.5,<2.0.0', 'pandas>=2.0.1,<3.0.0']

setup_kwargs = {
    'name': 'join-eos-exif',
    'version': '1.1.2',
    'description': 'Join EOS files to images using EXIF data',
    'long_description': '# joinEOStoEXIF\n\nApplication to join EOS and EXIF data files for image processing\n\nUI made with PyQt5 v5.14.1\nexe generated using Pyinstaller 3.4\n\n## Installation\n\n```sh\npip install -r requirements.txt\n```\n\n## Running\n\nUse join_data.exe or\n\n```sh\npython join_data.py\n```\n\n## Tests\n\nThe test.py file runs tests on sample input files stored in the sample_files folder.\n\nIt looks for one CSV and one txt file in each folder\n\n```sh\npython test.py\n```\n',
    'author': 'Taylor Denouden',
    'author_email': 'taylor.denouden@hakai.org',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8.1,<3.11',
}


setup(**setup_kwargs)
