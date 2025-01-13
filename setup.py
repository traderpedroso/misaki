from setuptools import setup, find_packages

setup(
    name='misaki',
    version='0.2.6',
    packages=find_packages(),
    package_data={
        'misaki': ['data/*.json'],
    },
    install_requires=[
        'num2words',
        'regex',
        'spacy',
        'spacy-curated-transformers',
    ],
    python_requires='>=3.7',
    author='hexgrad',
    author_email='hello@hexgrad.com',
    description='G2P engine for TTS',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/hexgrad/misaki',
    license='Apache 2.0',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
)