import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
    name="caplib4",
    version="0.1.1",
    author="Damien Marsic",
    author_email="damien.marsic@aliyun.com",
    description="Analysis of capsid libraries",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/damienmarsic/caplib4",
    package_dir={'': 'caplib4'},
    packages=setuptools.find_packages(),
    py_modules=["caplib4"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    python_requires='>=3.6',
)
