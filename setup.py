from setuptools import setup

setup(name='fortunebot',
      version='1.0',
      description="IRC bot for UCLA LUG",
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 2.7',
      ],
      url="https://github.com/EaterOA/fortunebot",
      author="Vincent Wong",
      author_email="duperduper@ucla.edu",
      license="GPL3",
      packages=["fortunebot", "fortunebot.daemon", "fortunebot.bot", "fortunebot.scripts"],
      install_requires=["irc"],
      zip_safe=False
     )
