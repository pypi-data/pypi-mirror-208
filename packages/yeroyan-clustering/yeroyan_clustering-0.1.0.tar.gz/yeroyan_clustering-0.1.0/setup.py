#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [ ]

test_requirements = ['pytest>=3', ]

setup(
    author="Ara Yeroyan",
    author_email='ar23yeroyan@gmail.com',
    python_requires='>=3.10',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    description="Automated Clustering and Anomaly Detection",
    install_requires=requirements,
    license="Apache Software License 2.0",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='yeroyan_clustering',
    name='yeroyan_clustering',
    packages=find_packages(include=['yeroyan_clustering', 'yeroyan_clustering.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/Ara-Yeroyan/yeroyan_clustering',
    version='0.1.0',
    zip_safe=False,
)
