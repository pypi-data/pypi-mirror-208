#Markdown Guide :

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="CNNtech_News",
    version="0.1.4",
    author="Hasan Gani Rachmatullah",
    author_email="ganirh0612@gmail.com",
    description="This package will provide you the most update of CNN Tech News",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ganirh0612/CNNtech_News",
    project_urls={
        "Bug Tracker": "https://github.com/pypa/sampleproject/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    #package_dir={"": "src"},
    #packages=setuptools.find_packages(where="src"),
    packages=setuptools.find_packages(),
    python_reuires=">=3.6"
)