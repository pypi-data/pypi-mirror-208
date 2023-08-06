import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="al2var",
    version="0.0.6",
    author="Jo Hendrix",
    author_email="jrhendrix36@gmail.com",
    description="Identify and calculate find variant rate between a bacterial genome sequence and either paired-end reads or another genome sequence",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jrhendrix/al2var",
    scripts=['bin/al2var'],
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)