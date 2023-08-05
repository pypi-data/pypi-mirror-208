from setuptools import setup

# read the contents of README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
  name = 'django-cloudspotlicense',         
  packages=['django_cloudspotlicense', 'django_cloudspotlicense.migrations', 'django_cloudspotlicense.templatetags'],
  include_package_data=True,
  version = '5.4.1',
  license='GPL-3.0-or-later',
  description = 'Django package to integrate the authentication of the Cloudspot License Server in other django applications',
  long_description=long_description,
  long_description_content_type='text/markdown',
  author = 'Alexander Schillemans',
  author_email = 'alexander.schillemans@lhs.global',
  url = 'https://github.com/Ecosy-EU/django-cloudspotlicense',
  download_url = 'https://github.com/Ecosy-EU/django-cloudspotlicense/archive/refs/tags/5.4.1.tar.gz',
  keywords = ['cloudspot', 'django'],
  install_requires=[
          'requests',
          'cloudspot-license-api',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    'Programming Language :: Python :: 3.6',
  ],
)