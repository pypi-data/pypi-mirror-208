
from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = [line.strip() for line in f.readlines()]

setup(
    name="knowledgebase-gsheet-gpt",
    version="1.0.0",
    packages=find_packages(),
    py_modules=['knowledgebase_gsheet_gpt'],
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'knowledgebase_gsheet_gpt = knowledgebase_gsheet_gpt:main',
        ],
    },
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',)
