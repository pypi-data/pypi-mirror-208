from setuptools import setup, find_packages

setup(
    name='HoodHod',
    version='0.2.0',
    description='A package for performing simple linear regression and binary decision tree classification and visualize the tree.',
    author="Derradji Aicha Elbatoul",
    author_email="derradjiaichaelbatoul@gmail.com",
    packages=find_packages(),
    install_requires=[
        'numpy',
        'graphviz',
        'prettytable'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
