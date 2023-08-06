import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="kable",
    version="0.0.1",
    author="Jo Hendrix",
    author_email="jrhendrix36@gmail.com",
    description="A tool for sequence, annotation, and methylome comparison between multiple bacterial genomes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jrhendrix/kable",
    scripts=['bin/kable'],
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=['python-Levenshtein', 'bio'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)