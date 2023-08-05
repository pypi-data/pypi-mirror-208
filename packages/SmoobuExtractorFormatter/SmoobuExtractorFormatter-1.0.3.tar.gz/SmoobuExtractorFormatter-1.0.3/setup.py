from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Operating System :: OS Independent',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

setup(
    name='SmoobuExtractorFormatter',
    version='1.0.3',
    description='A library to format the output of the Smoobu application',
    long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
    uri='',
    author='Badji Rayane',
    author_email='rayanebadji.freelance@gmail.com',
    license='MIT',
    classifiers=classifiers,
    keywords='Smoobu',
    packages=['SmoobuExtractorFormatter'],
    install_requires=['pandas','numpy','openpyxl','xlrd','requests']
)