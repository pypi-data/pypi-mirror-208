import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="xerxes-protocol",
    version="1.4.2a1",
    author="Stanislav Rubint",
    author_email="stanislav@rubint.sk",
    description="Python implementation for xerxes-protocol",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/metrotech-sk/xerxes-protocol",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
    ],
    entry_points = {
        'console_scripts': ['xerxes_config=xerxes_protocol.cli_util:address_config'],
    },
    python_requires='>=3.8',
)