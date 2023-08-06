from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Operating System :: Microsoft :: Windows :: Windows 10',
]

setup(
    name="Simplified JSON DICT LIST printer",
    version='0.0.1',
    description='Basic functions for printing and debugging',
    long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
    url='',
    author='Peter Nguyen',
    author_email='pnguyenkhang@gmail.com',
    classifiers=classifiers,
    keywords='print',
    packages=find_packages(),
    install_requires=['']
)