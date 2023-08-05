
from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = [line.strip() for line in f.readlines()]

setup(
    name="csv-embeddings-creator",
    version="1.0.4",
    packages=find_packages(),
    py_modules=['csv_embeddings_creator'],
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'csv_embeddings_creator = csv_embeddings_creator:main',
        ],
    },
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',)
