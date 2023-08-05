
from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = [line.strip() for line in f.readlines()]

setup(
    name="google-sheet-downloader",
    version="v1.0.0",
    packages=find_packages(),
    py_modules=['google_sheet_downloader'],
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'google_sheet_downloader = google_sheet_downloader:main',
        ],
    },
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',)
