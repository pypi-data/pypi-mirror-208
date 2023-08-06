import setuptools

with open("README.md", "r", encoding = "utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "rexactor",
    version = "1.0",
    author = "Maya Kapoor",
    author_email = "mkapoor1@uncc.edu",
    description = "An automatic regular expression signature generator",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/mayakapoor/rexactor",
    project_urls = {
        "Bug Tracker": "https://github.com/mayakapoor/rexactor/issues",
        "Documentation": "https://rexactor.readthedocs.io/en/latest/"
    },
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
          'tapcap'
    ],
    package_dir = {"": "src"},
    packages = setuptools.find_packages(where="src"),
    py_modules=[
        "grex",
        "trex",
        "rexactor",
        "cli",
        "operators"
    ],
    python_requires = ">=3.6",
    entry_points={
        "console_scripts": [
            "rexactor = cli:main"
        ]
    }
)
