import re

import setuptools

with open("requirements.txt", encoding="utf-8") as r:
    requirements = [i.strip() for i in r]

with open("kynaylibs/version.py", "rt", encoding="utf8") as x:
    version = re.search(r'__version__ = "(.*?)"', x.read()).group(1)

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

name = "kynaylibs"
author = "naya1503"
author_email = "cosmospanas70@gmail.com"
description = "A Secure and Powerful Python-Pyrogram Based Library For Naya-Pyro."
license_ = "GNU AFFERO GENERAL PUBLIC LICENSE (v3)"
url = "https://github.com/naya1503/kynaylibs"
project_urls = {
    "Bug Tracker": "https://github.com/naya1503/kynaylibs/issues",
    "Documentation": "https://t.me/kynansupport",
    "Source Code": "https://github.com/naya1503/kynaylibs",
}
classifiers = [
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    "Operating System :: OS Independent",
]

setuptools.setup(
    name=name,
    version=version,
    author=author,
    author_email=author_email,
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=url,
    project_urls=project_urls,
    license=license_,
    packages=setuptools.find_packages(),
    install_requires=requirements,
    classifiers=classifiers,
    python_requires=">3.7, <3.11",
)
