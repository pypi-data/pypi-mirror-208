from pathlib import Path

from setuptools import setup, find_packages

this_directory = Path(__file__).parent
long_description = (this_directory / 'README.md').read_text()

setup(name='senabase-starterpack',
      version='0.1.8',
      description='senabase starterpack library',
      long_description=long_description,
      long_description_content_type='text/markdown',
      author='Jungkyu Park',
      author_email='parkssie@me.com',
      url='https://github.com/parkssie/senabase-starterpack',
      python_requires='>=3.10',
      packages=find_packages(".", exclude=["test"]),
      install_requires=[
          'psycopg2-binary>=2.9.1',
          'pyyaml>=6.0',
          'requests>=2.30.0',
      ])
