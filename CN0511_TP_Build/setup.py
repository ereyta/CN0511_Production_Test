import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="CN0511_Production_Test",
    version="0.0.1",
    author="Erbe Reyta",
    author_email="erbe.reyta@analog.com",
    description="CN0511 Test Procedure Package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ereyta/CN0511_Production_Test",
    project_urls={
        "Bug Tracker": "https://github.com/ereyta/CN0511_Production_Test/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)