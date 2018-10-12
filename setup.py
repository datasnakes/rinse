from setuptools import setup
setup(
    name = 'rinse',
    version = '0.1.0',
    packages = ['rinse'],
    entry_points = {
        'console_scripts': [
            'rinse = rinse.__main__:main'
        ]
    })