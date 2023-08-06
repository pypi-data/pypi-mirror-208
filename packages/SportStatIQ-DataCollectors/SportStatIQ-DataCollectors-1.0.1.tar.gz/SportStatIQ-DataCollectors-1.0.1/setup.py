from setuptools import setup, find_packages

setup(
    name='SportStatIQ-DataCollectors',
    version='1.0.1',
    description='Collects data from various sports websites',
    author='Matthew Myrick',
    author_email='MatthewMyrick2@gmail.com',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'requests',
        'bs4'
    ],
)
