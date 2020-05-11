from setuptools import setup

VERSION = ""
exec(open('settingsmanager/version.py').read())

setup(name='settingsmanager',
      version=VERSION,
      description='Settings File Manager',
      author='Rob Gossington',
      author_email='rgossington@gmail.com',
      url='https://github.com/rgossington/settings-manager',
      packages=['settingsmanager'],
      install_requires=[],
      )
