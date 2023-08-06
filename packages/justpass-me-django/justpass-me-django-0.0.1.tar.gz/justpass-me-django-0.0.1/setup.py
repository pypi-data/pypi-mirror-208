#!/usr/bin/env python

from setuptools import find_packages, setup

setup(
    name='justpass-me-django',
    version='0.0.1',
    description='Django Integration with JustPass.me',
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author='JustPassMe',
    author_email = 'sameh@justpass.me',
    url = 'https://github.com/justpass-me/justpass-me-django',
    download_url='https://github.com/justpass-me/justpass-me-django',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'django >= 2.0',
        'mozilla-django-oidc==3.0.0'
      ],
    python_requires=">=3.7",
    include_package_data=True,
    zip_safe=False, # because we're including static files
    classifiers=[
        #"Development Status :: 5 - Production/Stable",
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 2.0",
        "Framework :: Django :: 2.1",
        "Framework :: Django :: 2.2",
        "Framework :: Django :: 3.0",
        "Framework :: Django :: 3.1",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 4.1",
        "Framework :: Django :: 4.2",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
]
)
