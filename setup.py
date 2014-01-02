from setuptools import setup

setup(name='lugbot',
      version='0.1',
      description="IRC bot for UCLA LUG",
      url="https://github.com/EaterOA",
      author="Vincent Wong",
      author_email="duperduper@ucla.edu",
      license="GPL3",
      packages=["lugbot"],
      install_requires=["irc"],
      zip_safe=False
     )
