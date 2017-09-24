from setuptools import setup
from footprint import __version__

setup(
    name='footprint',
    version=__version__,
    install_requires=[
        'PyGithub'
    ],
    entry_points='''
        [console_scripts]
        footprint = cli:main
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
