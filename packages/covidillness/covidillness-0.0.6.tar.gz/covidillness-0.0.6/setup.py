import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="covidillness",
    version="0.0.6",
    author="Izuru Inose",
    author_email="i.inose0304@gmail.com",
    description="The graph of the number of ICU patients and deaths due to Covid-19",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/i-inose/covidillness",
    project_urls={
        "Bug Tracker": "https://github.com/i-inose/covidillness",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    py_modules=['covidillness'],
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.7",
    entry_points = {
        'console_scripts': [
            'covidillness = covidillness:main'
        ]
    },
)
