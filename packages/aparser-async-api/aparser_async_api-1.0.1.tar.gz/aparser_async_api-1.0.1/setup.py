import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

requirements = ['aiohttp>=3.8']

setuptools.setup(
    name='aparser_async_api',
    version='1.0.1',
    author='Utkin Artem',
    author_email='thesame.personal@gmail.com',
    description='Asyncio is an alternative module for working with A-parser.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/DvaMishkiLapa/aparser-async-api',
    packages=setuptools.find_packages(),
    install_requires=requirements,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)
