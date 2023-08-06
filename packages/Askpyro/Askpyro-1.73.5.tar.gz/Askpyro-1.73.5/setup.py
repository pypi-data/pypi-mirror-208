#  Askpyro - Easy conversation handler for pyrogram 
#  Copyright (C) 2023-present Abishnoi6 <https://github.com/Abishnoi69>
#
#  This file is part of Askpyro.
#
#  Askpyro is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Askpyro is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Askpyro.  If not, see <http://www.gnu.org/licenses/>.

# ===================================================================

import re
from sys import argv
import setuptools



with open("README.md", encoding="utf8") as readme:
    long_description = readme.read()
    
"""    
def read(file: str) -> list:
    with open(file, encoding="utf-8") as r:
        return [i.strip() for i in r]
"""

setuptools.setup(
    name="Askpyro",
    packages=setuptools.find_packages(),
    version="1.73.5",
    description="Easy conversation handler for pyrogram",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Abishnoi69",
    download_url="https://github.com/Abishnoi69/Askpyro/releases/latest",
    author="Abishnoi",
    author_email="abishnoi@askpyro.org",
    license="LGPLv3",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: Implementation",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Internet",
        "Topic :: Communications",
        "Topic :: Communications :: Chat",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries :: Application Frameworks"
    ],
    keywords="telegram chat messenger mtproto api client library python conversation",
    project_urls={
        "Tracker": "https://github.com/Abishnoi69/Askpyro/issues",
        "Community": "https://t.me/AbishnoiMF",
        "Source": "https://github.com/Abishnoi69/Askpyro",
        "Documentation": "https://github.com/Abishnoi69/askpyro/wiki",
    },
    python_requires="~=3.7",
    zip_safe=False,
    # install_requires=read("requirements.txt")
)
