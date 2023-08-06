#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()


requirements=[]
test_requirements = ['pytest>=3', ]

setup(
    author="Anahit Zakaryan",
    author_email='anukzak@gmail.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="This is a package containing several bass model functions that are useful for solving or evaluating marketing related problems ",
    install_requires=requirements,
    license="MIT license",
    long_description=readme ,
    include_package_data=True,
    keywords='markbassmodel',
    name='markbassmodel',
    packages=find_packages(include=['markbassmodel', 'markbassmodel.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/anukzak22/markbassmodel',
    version='0.1.1',
    zip_safe=False,
)
