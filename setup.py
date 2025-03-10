import os
import shutil
from setuptools import setup, find_packages

def clean_pycache():
    for root, dirs, files in os.walk("."):
        if "__pycache__" in dirs:
            pycache_path = os.path.join(root, "__pycache__")
            shutil.rmtree(pycache_path)
            print(f"Supprimé : {pycache_path}")

clean_pycache()

setup(
    name='rambot',
    version='0.1.2',
    packages=find_packages(where='.', exclude=["*__pycache__*"]),
    url='https://github.com/AlexVachon/rambot',
    license='MIT',
    author='Alexandre Vachon',
    author_email='alex.vachon@outlook.com',
    description='Configurable web scraping framework designed to automate data extraction from web pages',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    python_requires='>=3.8',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License'
    ],
    package_data={
        '': ['*.md', '*.txt'],
    },
    include_package_data=True,
)
