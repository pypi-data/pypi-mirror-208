from distutils.core import setup
from setuptools import find_packages

with open('README.rst', 'r') as f:
    long_description = f.read()

setup(name='zcbot-predict-sdk',
      version='0.0.17',
      description='zcbot predict sdk for zsodata',
      long_description=long_description,
      author='zsodata',
      author_email='team@zso.io',
      url='http://www.zsodata.com',
      install_requires=['celery', 'redis'],
      python_requires='>=3.7',
      license='BSD License',
      packages=find_packages(),
      platforms=['all'],
      include_package_data=True
      )
