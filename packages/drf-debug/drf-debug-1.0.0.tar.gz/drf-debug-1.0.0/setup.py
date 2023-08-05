import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="drf-debug",
    version="1.0.0",
    author="Mohammad Dori",
    author_email="mr.dori.dev@gmail.com",
    description="API tracking package.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dori-dev/drf-debug",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    install_requires=[
        "Django>=3.2",
        "djangorestframework>=3.11",
    ],
    python_requires=">=3.6",
)
