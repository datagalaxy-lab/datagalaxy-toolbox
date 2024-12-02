from setuptools import setup, find_packages
from toolbox import __version__

setup(name='toolbox',
      version=__version__,
      author='DataGalaxy',
      author_email='opencode@datagalaxy.com',
      python_requires='>=3.9',
      packages=find_packages(),
      install_requires=['requests==2.32.3', 'PyJWT==2.10.1']
      )
