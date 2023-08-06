from setuptools import setup
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
  name = 'ipv64',
  version = '0.5.0',
  description = 'Updater for ipv64.net - ATTENTION THIS VERSION IS NOT COMPATIBLE WITH THE 0.4.2!',
  author = 'R60',
  author_email = 'pypi.nmvk0@getrekt.win',
  url = 'https://github.com/syncip/ipv64',
  py_modules=["ipv64"],
  package_dir={'': 'src'},
  keywords = ['ipv64', 'dyndns', 'updater'],
  long_description=long_description,
  long_description_content_type='text/markdown',
  install_requires=['requests==2.28.1',
                    'argparse==1.4.0',
                    ],
)