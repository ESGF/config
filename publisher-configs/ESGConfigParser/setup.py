#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

from ESGConfigParser.constants import VERSION

setup(name='ESGConfigParser',
      version=VERSION,
      description='ESGF configuration ESGConfigParser for INI files',
      author='Levavasseur Guillaume',
      author_email='glipsl@ipsl.fr',
      url='https://github.com/IS-ENES-Data/esgf-config-esgini',
      packages=find_packages(),
      platforms=['Unix'],
      zip_safe=False,
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Environment :: Console',
                   'Intended Audience :: Science/Research',
                   'Intended Audience :: System Administrators',
                   'Natural Language :: English',
                   'Operating System :: Unix',
                   'Programming Language :: Python',
                   'Topic :: Scientific/Engineering',
                   'Topic :: Software Development :: Build Tools']
      )
