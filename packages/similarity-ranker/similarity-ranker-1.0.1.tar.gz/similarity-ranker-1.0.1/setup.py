
from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = [line.strip() for line in f.readlines()]

setup(
    name="similarity-ranker",
    version="1.0.1",
    packages=find_packages(),
    py_modules=['similarity_ranker'],
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'similarity_ranker = similarity_ranker:main',
        ],
    },
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',)
