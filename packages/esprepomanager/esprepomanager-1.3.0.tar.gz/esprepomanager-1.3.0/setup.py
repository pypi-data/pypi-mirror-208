import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="esprepomanager",
    version="1.3.0",
    author="Teichi",
    author_email="tobias@teichmann.top",
    description="manager for git repos",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.tugraz.at/esp-oop1-dev/pyrepomanager",
    packages=setuptools.find_packages(),
    entry_points={"console_scripts": ["esprepomanager=esprepomanager:main"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    install_requires=['requests', 'toml'],
)
