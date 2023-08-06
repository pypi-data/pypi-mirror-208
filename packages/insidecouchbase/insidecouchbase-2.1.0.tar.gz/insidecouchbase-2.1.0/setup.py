import setuptools

with open("README.md", "r", encoding = "utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "insidecouchbase",
    version = "2.1.0",
    author = "Huseyin Demir",
    author_email = "huseyin.d3r@gmail.com",
    description = "Check and analyze a couchbase cluster in terms of cluster health,bucket,and replication",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/adiosamig/insidecocuhbase",
    install_requires=[
        'requests',
        'tabulate',
        'pandas',
        'requests'
    ],
    project_urls = {
        "Bug Tracker": "https://github.com/adiosamig/insidecocuhbase/issues",
    },
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir = {"": "src"},
    packages = setuptools.find_packages(where="src"),
    python_requires = ">=3.6"
)