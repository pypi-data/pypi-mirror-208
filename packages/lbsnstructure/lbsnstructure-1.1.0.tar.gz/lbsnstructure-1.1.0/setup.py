# -*- coding: utf-8 -*-

"""Setuptools config file
"""

from setuptools import setup
import sys

with open('README.md') as f:
    long_description = f.read()

try:
    from semantic_release import setup_hook
    setup_hook(sys.argv)
except ImportError:
    pass

version = {}
with open("lbsnstructure/version.py") as fp:
    exec(fp.read(), version)

setup(name='lbsnstructure',
      version=version['__version__'],
      description='A common language independent and cross-network social-media data scheme.',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://gitlab.vgiscience.de/lbsn/concept',
      author='Filip Krumpe; Alexander Dunkel; Marc Löchner',
      author_email='alexander.dunkel@tu-dresden.de',
      license='MIT',
      packages=['lbsnstructure'],
      install_requires=[
          'protobuf',
      ],
      zip_safe=False)
