#!/usr/bin/env python3
from setuptools import setup, find_packages

# long description with latest release notes
long_description = readme = open('README.rst').read()
#news = open('NEWS.rst').read()
#long_description = (readme + "\n\nLatest release notes\n====================\n"
#                    + '\n'.join(news.split('\n\n\n', 1)[0].splitlines()[2:]))

# the actual setup
setup(name='clickmaster2000', version='1.1',
      description='Tally counter for images',

      author="Yuri D'Elia",
      author_email="wavexx@thregr.org",
      license="GPLv3+",
      long_description=long_description,
      url="https://www.thregr.org/~wavexx/projects/clickmaster2000/",
      keywords='tally counter image microbiology',
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Environment :: Win32 (MS Windows)',
                   'Environment :: Environment :: MacOS X',
                   'Environment :: X11 Applications :: Qt',
                   'Intended Audience :: Science/Research',
                   'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 3',
                   'Topic :: Scientific/Engineering',
                   'Topic :: Utilities'],

      entry_points={'gui_scripts': ['clickmaster2000=clickmaster2000:main']},
      packages=find_packages(),
      include_package_data=True,
      setup_requires=['setuptools'])
