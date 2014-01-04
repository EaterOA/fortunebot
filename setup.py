from setuptools import setup

setup(name='fortunebot',
      version='0.1',
      description="IRC bot for UCLA LUG",
      url="https://github.com/EaterOA/fortunebot",
      author="Vincent Wong",
      author_email="duperduper@ucla.edu",
      license="GPL3",
      packages=["fortunebot"],
      install_requires=["irc"],
      zip_safe=False
     )
