# -*- coding: utf-8 -*-
import sys
import setuptools



INSTALL_PYTHON_REQUIRES = []
# We are intending to keep up to date with the supported Django versions.
# For the official support, please visit:
# https://docs.djangoproject.com/en/4.0/faq/install/#what-python-version-can-i-use-with-django
if sys.version_info[1] in [8, 9, 10, 11]:
    django_python_version_install = "Django>=4.0.4"
    INSTALL_PYTHON_REQUIRES.append(django_python_version_install)

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='AkvoDjangoFormGateway',
    author="Akvo",
    author_email="tech.consultancy@akvo.org",
    maintainer="Deden Bangkit",
    maintainer_email="deden@akvo.org",
    description="A Django library that enables seamless integration of messenger services",
    keywords='akvo, twilio, whatsapp, ssid, sms, django',
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    zip_safe=False,
    include_package_data=True,
    url='https://github.com/akvo/Akvo-DjangoFormGateway',
    project_urls={
        "Documentation": "https://github.com/akvo/Akvo-DjangoFormGateway",
        "Bug Reports": "https://github.com/akvo/Akvo-DjangoFormGateway/issues",
        "Source Code": "https://github.com/akvo/Akvo-DjangoFormGateway",
    },
    classifiers=[
        # https://pypi.org/classifiers/
        "Development Status :: 4 - Beta",
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Framework :: Django',
        'Framework :: Django :: 4.0',
        'Framework :: Django :: 4.1',
        "Operating System :: OS Independent",
        'Topic :: Internet :: WWW/HTTP',
    ],
    python_requires=">=3.8.5",
    install_requires=[
        'setuptools>=36.2',
        'twilio>=8.2.0',
        'djangorestframework>=3.12.4',
    ] + INSTALL_PYTHON_REQUIRES,
    extras_require={
        "dev": ["check-manifest"],
    },

)
