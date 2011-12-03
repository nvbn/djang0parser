from setuptools import setup, find_packages
import sys, os

version = '0.3'

setup(name='djang0parser',
      version=version,
      description="html sanitiezer from djang0byte",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='django',
      author='Vladimir Yakovlev',
      author_email='nvbn.rm@gmail.com',
      url='https://github.com/nvbn/djang0parser',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'BeautifulSoup', 'Pygments',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
