from setuptools import find_packages, setup

# injected version
__version__ = "0.1.3"

# markdown readme
long_description = open("README.md").read()

# read requirements from requirements.in
install_requires = open("requirements.in").read().splitlines()

setup(
    name="cici.tools",
    version=__version__,
    author="Brett Weir",
    author_email="brett@brettops.io",
    description="CI pipeline toolkit.",
    license="MIT",
    url="https://gitlab.com/brettops/tools/cici",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "cici = cici.__main__:main",
        ],
    },
    install_requires=install_requires,
    python_requires=">=3.6",
    keywords="ci pipeline python",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
