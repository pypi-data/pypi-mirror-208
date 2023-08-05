from setuptools import setup

long_description = open('README.rst').read()

setup(name="pyGuardPoint",
      version="0.9.1",
      author="John Owen",
      description="Python wrapper for GuardPoint 10 Access Control System",
      long_description_content_type='text/markdown',
      long_description=long_description,
      maintainer_email="sales@sensoraccess.co.uk",
      install_requires=['validators', 'fuzzywuzzy', 'Levenshtein'],
      packages=['pyGuardPoint'],
      license_files=('LICENSE.txt',),
      zip_safe=False)
