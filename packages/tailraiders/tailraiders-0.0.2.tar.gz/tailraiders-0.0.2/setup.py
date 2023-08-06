from setuptools import setup, find_packages

setup(
    author = 'Busse Heemskerk',
    description = 'A package for making Data Science easier, versions with 0.0.x are trials and tests',
    long_description = open('README.md').read(),
    long_description_content_type = 'text/markdown',
    name = 'tailraiders',
    version = '0.0.2',
    packages = find_packages(include = ['tailraiders', 'tailraiders.*']),
    install_requires = ['pandas>=1.0',
                        'numpy>=1.0',
                        'matplotlib>=2.2.3',
                        'seaborn>=0.9.0'],
    python_requires = '>=2.7, !=3.0.*, !=3.1.*'
    )