from setuptools import setup

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='finny_scraper',
    version='0.9',
    description='A package for scraping property information from Finny website',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/samueltanner/rfin_scraper',
    packages=['finny_scraper'],
    install_requires=[
        'beautifulsoup4',
        'requests'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)

# to push changes to pypi
# python setup.py sdist bdist_wheel
# twine upload dist/*
