import setuptools

with open("README.md", "r", encoding = "utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "tapcap",
    version = "1.0",
    author = "Maya Kapoor",
    author_email = "mkapoor1@uncc.edu",
    description = "A network packet tabularization tool",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/mayakapoor/tapcap",
    project_urls = {
        "Bug Tracker": "https://github.com/mayakapoor/tapcap/issues",
        "Documentation": "https://tapcap.readthedocs.io/en/latest/"
    },
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires = ">=3.6",
    entry_points={
        "console_scripts": [
            "tapcap = tapcap:main"
        ]
    }
)
