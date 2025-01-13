from setuptools import setup, find_packages

setup(
    name='misaki',
    version='0.3.5',
    packages=find_packages(),
    package_data={
        'misaki': ['data/*.csv', 'data/*.json', 'data/*.tsv', 'data/*.txt'],
    },
    install_requires=[
        'num2words',
        'regex',
        'spacy',
        'spacy-curated-transformers',
        'fugashi',
        'g2pk2',
        'jaconv',
        'jieba',
        'mojimoji',
        'ordered-set',
        'pypinyin',
        'unicodedata2',
        'unidic-lite',
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