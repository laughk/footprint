from setuptools import setup, find_packages
from footprint import __version__

# Get the long description from the README file
with open('README.rst', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='footprint',
    description='footpritnt(足跡) is summary generator for Github/Gitlab.com activity.',
    long_description=long_description,
    version=__version__,
    packages=find_packages(),
    install_requires=[
        'PyGithub',
        'python-dateutil',
        'tzlocal',
    ],
    entry_points='''
        [console_scripts]
        footprint = footprint.cli:main
    ''',
    url='https://github.com/laughk/footprint',
    author='Kei Iwasaki',
    author_email='me@laughk.org',
    license='MIT License',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ]
)
