import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="latestinfoearthquakeindonesia",
    version="0.0.3",
    author="Hendra Go",
    author_email="hendrago91@gmail.com",
    description="This package will get the latest earthquake from BMKG | Meteorological, Climatological, and "
                "Geophysical Agency.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TOSS-ID/latest-indonesia-earthquake",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable"
    ],
    python_requires='>=3.6',
)
