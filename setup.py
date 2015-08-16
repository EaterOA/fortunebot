from setuptools import setup, find_packages

setup(
    name='fortunebot',
    version='1.3',
    description='Yet another IRC bot',
    classifiers=[
      'Development Status :: 4 - Beta',
      'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
      'Programming Language :: Python :: 2.7',
      'Programming Language :: Python :: 3.4',
    ],
    url='https://github.com/EaterOA/fortunebot',
    author='Vincent Wong',
    author_email='duperduper@ucla.edu',
    license='GPL3',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'irc>=11',
        'appdirs',
        'requests',
        'six',
        'nose',
        'mock',
    ],
    entry_points={
        'console_scripts': [
            'fortunebot = fortunebot.botrunner:main',
            'fortunebot-generate-config = fortunebot.generate_config:main',
        ],
    },
)
